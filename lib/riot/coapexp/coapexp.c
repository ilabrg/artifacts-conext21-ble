
#include <stdlib.h>

#include "msg.h"
#include "tsrb.h"
#include "shell.h"
#include "random.h"
#include "thread.h"
#include "thread_flags.h"
#include "net/gcoap.h"
#include "net/ipv6/addr.h"
#include "net/bluetil/addr.h"

#ifdef MODULE_MYPRINT
#include "myprint.h"
#else
#define myputs(x)       puts(x)
#define myprintf(...)   printf(__VA_ARGS__)
#endif
#include "expstats.h"

#ifdef MODULE_PROCDELAY
#include "procdelay.h"
#endif

#define PATH                    "/myexp/getres"

#define APP_BUFLEN              (1500U)
#define CTX_NUMOF               (14U)

#define WORKER_PRIO             (THREAD_PRIORITY_MAIN + 1)

#define MAIN_QUEUE_SIZE (8)

#ifndef EXPSTATS_MIN_LEN
#define EXPSTATS_MIN_LEN        (10U)
#endif

static int _active = 0;

typedef struct {
    event_t e;
    event_timeout_t et;
    uint32_t t_min;
    uint32_t t_max;
    uint32_t duration;
    uint32_t elapsed;
    sock_udp_ep_t remote;
    uint16_t paylen_req;
    uint16_t paylen_resp;
    uint32_t seq;
    unsigned method;
    int confirmable;
    struct {
        unsigned evts;
        unsigned ok;
        unsigned er;
    } cnt;
} prod_ctx_t;

static prod_ctx_t _ctx[CTX_NUMOF];

static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

static char _worker_stack[THREAD_STACKSIZE_DEFAULT];
static event_queue_t _worker_q;

static uint8_t _txbuf[APP_BUFLEN];

static ssize_t _req_handler(coap_pkt_t* pdu, uint8_t *buf, size_t len, void *ctx)
{
    (void)ctx;

    if (pdu->payload_len < EXPSTATS_MIN_LEN) {
        return 0;
    }

    uint16_t paylen = expstats_buf_get_paylen(pdu->payload, (size_t)pdu->payload_len);
    uint32_t seq = expstats_buf_get_seq(pdu->payload, (size_t)pdu->payload_len);

#ifdef MODULE_PROCDELAY
    procdelay_print(seq, PROCDELAY_RECEIVE);
#endif
    expstats_log_seq(EXPSTATS_APP_RX, seq);

    if (coap_method2flag(coap_get_code_detail(pdu)) == COAP_GET) {
        gcoap_resp_init(pdu, buf, len, COAP_CODE_CONTENT);
        coap_opt_add_format(pdu, COAP_FORMAT_TEXT);
    }
    else {
        gcoap_resp_init(pdu, buf, len, COAP_CODE_CHANGED);
    }
    size_t hdr_len = coap_opt_finish(pdu, COAP_OPT_FINISH_PAYLOAD);
    if (paylen > pdu->payload_len) {
        myputs("[prod] er: unable to fit reply into buffer");
        return 0;
    }

    seq = expstats_mark_reply(seq);
    expstats_mk_pkt(pdu->payload, (size_t)paylen, seq, 0);
    return hdr_len + paylen;
}

static void _on_resp(const gcoap_request_memo_t *memo, coap_pkt_t* pdu,
                     const sock_udp_ep_t *remote)
{
    (void)pdu;
    (void)remote;

    unsigned seq = (unsigned)memo->context;

    switch (memo->state) {
        case GCOAP_MEMO_TIMEOUT:
            expstats_log_seq(EXPSTATS_APP_ACK_TO, seq);
            break;
        case GCOAP_MEMO_ERR:
            expstats_log_seq(EXPSTATS_APP_ACK_ER, seq);
            break;
        default: {
            if (pdu->payload_len < EXPSTATS_MIN_LEN) {
                myputs("[prod] er: resp has invalid payload len");
                return;
            }
            uint32_t seq = expstats_buf_get_seq(pdu->payload, pdu->payload_len);
#ifdef MODULE_PROCDELAY
            procdelay_print(seq, PROCDELAY_RECEIVE);
#endif
            expstats_log_seq(EXPSTATS_APP_ACK, seq);
            break;
        }
    }
}

static void *_worker(void *arg)
{
    (void)arg;
    event_queue_init(&_worker_q);

    while (1) {
        event_loop(&_worker_q);
    }

    return NULL;
}

static void _sched_next(prod_ctx_t *ctx)
{

    uint32_t next_to = random_uint32_range(ctx->t_min, ctx->t_max + 1);
    ctx->elapsed += (next_to / 1000);
    if (ctx->elapsed <= ctx->duration) {
        event_timeout_set(&ctx->et, next_to);
    }
    else {
        char ip[IPV6_ADDR_MAX_STR_LEN];
        ipv6_addr_to_str(ip, (ipv6_addr_t *)&ctx->remote.addr.ipv6, IPV6_ADDR_MAX_STR_LEN);

        myprintf("[prod] FINISHED remote:%s paylen_req:%u paylen_resp:%u dur:%u last_seq:%u-%u"
                 " evts:%u ok:%u er:%u\n",
                 ip,
                 (unsigned)ctx->paylen_req, (unsigned)ctx->paylen_resp,
                 (unsigned)ctx->duration,
                 expstats_get_id(ctx->seq), expstats_get_seq(ctx->seq),
                 ctx->cnt.evts, ctx->cnt.ok, ctx->cnt.er);
        ctx->t_max = 0;
        _active = 0;
    }
}

static void _send_evt(event_t *evt)
{
    coap_pkt_t pdu;
    prod_ctx_t *ctx = (prod_ctx_t *)evt;

    ctx->cnt.evts++;

    /* prepare packet */
    gcoap_req_init(&pdu, _txbuf, sizeof(_txbuf), ctx->method, PATH);
    if (ctx->confirmable) {
        coap_hdr_set_type(pdu.hdr, COAP_TYPE_CON);
    }
    size_t hdr_len = (size_t)coap_opt_finish(&pdu, COAP_OPT_FINISH_PAYLOAD);

    ctx->seq = expstats_inc_seq(ctx->seq);
    expstats_mk_pkt(pdu.payload, ctx->paylen_req, ctx->seq, ctx->paylen_resp);

    expstats_log_seq(EXPSTATS_APP_TX, ctx->seq);
#ifdef MODULE_PROCDELAY
    procdelay_time(ctx->seq, PROCDELAY_SEND);
#endif
    size_t res = gcoap_req_send(_txbuf, (hdr_len + ctx->paylen_req),
                                &ctx->remote, _on_resp, (void *)ctx->seq);
    if (res > 0) {
        ctx->cnt.ok++;
    }
    else {
        expstats_log_seq(EXPSTATS_APP_TX_ERR, ctx->seq);
        ctx->cnt.er++;
    }

    _sched_next(ctx);
}

static prod_ctx_t *_get_ctx(void)
{
    for (unsigned i = 0; i < CTX_NUMOF; i++) {
        if (_ctx[i].t_max == 0) {
            return &_ctx[i];
        }
    }

    return NULL;
}

static int _run(int argc, char **argv, unsigned method, int confirmable)
{
    if (argc < 7) {
        myprintf("usage: %s <dst addr> <seq id> <pkt_len [byte]> <duration [s]> <itvl [ms]> <jitter [ms]>\n",
                 argv[0]);
        return 1;
    }

    if (_active == 1) {
        myprintf("error: COMMAND already running!\n");
        return 1;
    }
    _active = 1;

    prod_ctx_t *ctx = _get_ctx();
    if (ctx == NULL) {
        myputs("error: no free prod context");
        return 1;
    }
    memset(ctx, 0, sizeof(prod_ctx_t));

    ctx->remote.family = AF_INET6;
    ctx->remote.port = COAP_PORT;
    ipv6_addr_t *addr = ipv6_addr_from_str((ipv6_addr_t *)&ctx->remote.addr.ipv6, argv[1]);
    assert(addr != NULL);
    (void)addr;

    unsigned itvl = (unsigned)atoi(argv[5]);
    unsigned jitter = (unsigned)atoi(argv[6]);

    ctx->t_min = (uint32_t)((itvl * 1000) - ((jitter + 0) * 1000));
    ctx->t_max = (uint32_t)((itvl * 1000) + ((jitter + 0) * 1000));
    ctx->duration = (uint32_t)atoi(argv[4]) * 1000;
    ctx->elapsed = 0;
    ctx->seq = expstats_mk_seq(0, (uint8_t)atoi(argv[2]));
    ctx->method = method;
    ctx->confirmable = confirmable;

    if (method == COAP_METHOD_GET) {
        ctx->paylen_req = EXPSTATS_MIN_LEN;
        ctx->paylen_resp = (uint16_t)atoi(argv[3]);
    }
    else {
        ctx->paylen_req = (uint16_t)atoi(argv[3]);
        ctx->paylen_resp = EXPSTATS_MIN_LEN;
    }

    myprintf("[prod] START\n");

    ctx->e.handler = _send_evt;
    event_timeout_init(&ctx->et, &_worker_q, &ctx->e);

    _sched_next(ctx);
    return 0;
}

static int _cmd_put_non(int argc, char **argv)
{
    return _run(argc, argv, COAP_METHOD_PUT, 0);
}

static int _cmd_put_con(int argc, char **argv)
{
    return _run(argc, argv, COAP_METHOD_PUT, 1);
}

static int _cmd_get_non(int argc, char **argv)
{
    return _run(argc, argv, COAP_METHOD_GET, 0);
}

static int _cmd_get_con(int argc, char **argv)
{
    return _run(argc, argv, COAP_METHOD_GET, 1);
}

static const coap_resource_t _resources[] = {
    { PATH, COAP_GET | COAP_PUT, _req_handler, NULL },
};

static gcoap_listener_t _listener = {
    &_resources[0], ARRAY_SIZE(_resources), NULL, NULL, NULL
};

static const shell_command_t _cmds[] = {
    { "put-non", "producer: PUT NON", _cmd_put_non },
    { "put-con", "producer: PUT CON", _cmd_put_con },
    { "get-non", "consumer: GET NON", _cmd_get_non },
    { "get-con", "consumer: GET CON", _cmd_get_con },
    { NULL, NULL, NULL }
};

void coapexp_run(void)
{
    memset(_ctx, 0, sizeof(_ctx));

    gcoap_register_listener(&_listener);

    thread_create(_worker_stack, sizeof(_worker_stack), WORKER_PRIO,
                  THREAD_CREATE_STACKTEST, _worker, NULL, "send_worker");

    /* start shell */
    msg_init_queue(_main_msg_queue, sizeof(_main_msg_queue));
    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(_cmds, line_buf, SHELL_DEFAULT_BUFSIZE);
}
