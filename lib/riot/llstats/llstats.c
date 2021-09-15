
#include <stdlib.h>
#include <string.h>

#include "ztimer.h"
#include "fmt.h"

#include "myprint.h"
#include "llstats.h"
#include "nimble_netif_conn.h"

#define STARTUP_DELAY       (2 * 1000U)
#define INTERVAL            (5 * 1000U)
#define CHAR_NA             '-'

#define PRIO                (THREAD_PRIORITY_MAIN + 2)
static char _stack[THREAD_STACKSIZE_DEFAULT];

static const char _charmap[62] = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
static char _outtext[81];

// extern struct ble_ll_conn_sm g_ble_ll_conn_sm[MYNEWT_VAL_BLE_MAX_CONNECTIONS];
// static struct ble_ll_conn_sm _smtmp[MYNEWT_VAL_BLE_MAX_CONNECTIONS];

static char _map_u32(unsigned cnt)
{
    if (cnt >= sizeof(_charmap)) {
        return CHAR_NA;
    }
    return _charmap[cnt];
}

llstats_t llstats[MYNEWT_VAL_BLE_MAX_CONNECTIONS];
llstats_phy_t llstats_phy;

// static void _dump_conn_offset(void)
// {
//     unsigned pos = 0;

//     unsigned is = irq_disable();
//     memcpy(_smtmp, g_ble_ll_conn_sm, sizeof(_smtmp));
//     irq_restore(is);

//     for (unsigned i = 0; i < MYNEWT_VAL_BLE_MAX_CONNECTIONS; i++) {
//         struct ble_ll_conn_sm *sm = &_smtmp[i];

//         if (sm->conn_role > 0) {
//             int handle = nimble_netif_conn_get_by_gaphandle(sm->conn_handle);
//             _outtext[pos++] = 'c';
//             pos += fmt_u16_dec(&_outtext[pos], (uint16_t)handle);
//             if (CONN_IS_MASTER(sm)) {
//                 _outtext[pos++] = 'M';
//             }
//             else {
//                 _outtext[pos++] = 'S';
//             }
//             pos += fmt_u32_dec(&_outtext[pos], sm->anchor_point);
//         }
//     }
//     _outtext[pos] = '\0';
//     myprintf("ll-%s\n", _outtext);
// }

static void _dump(void)
{
    llstats_t tmp;

    for (unsigned i = 0; i < MYNEWT_VAL_BLE_MAX_CONNECTIONS; i++) {
        if (llstats[i].used == 1) {
            unsigned is = irq_disable();
            memcpy(&tmp, &llstats[i], sizeof(llstats_t));
            memset(&llstats[i], 0, sizeof(llstats_t));
            irq_restore(is);

            unsigned pos = 0;
            for (unsigned c = 0; c < BLE_CHAN_NUMOF; c++) {
                _outtext[pos++] = _map_u32(tmp.chan[c].tx);
                _outtext[pos++] = _map_u32(tmp.chan[c].ok);
            }
            _outtext[pos] = '\0';
            myprintf("ll%u,%s\n", (i + 1), _outtext);
        }
    }
}

static void _dump_phy(void)
{
    uint32_t rx;
    uint32_t tx;
    uint32_t itvl_start;
    uint32_t now = ztimer_now(ZTIMER_USEC);
    uint32_t rx_cnt;
    uint32_t rx_cnt_off;
    uint32_t tx_cnt;
    uint32_t tx_cnt_off;

    /* copy stats */
    unsigned is = irq_disable();
    rx = llstats_phy.rx;
    llstats_phy.rx = 0;
    tx = llstats_phy.tx;
    llstats_phy.tx = 0;
    itvl_start = llstats_phy.itvl_start;
    llstats_phy.itvl_start = now;

    rx_cnt = llstats_phy.rx_cnt;
    llstats_phy.rx_cnt = 0;
    rx_cnt_off = llstats_phy.rx_cnt_off;
    llstats_phy.rx_cnt_off = 0;
    tx_cnt = llstats_phy.tx_cnt;
    llstats_phy.tx_cnt = 0;
    tx_cnt_off = llstats_phy.tx_cnt_off;
    llstats_phy.tx_cnt_off = 0;

    irq_restore(is);

    uint32_t itvl = now - itvl_start;
    myprintf("ll,%u,%u,%u,%u,%u,%u,%u,%u\n",
             (unsigned)itvl,
             (unsigned)rx_cnt, (unsigned)rx,
             (unsigned)tx_cnt, (unsigned)tx,
             (unsigned)os_msys_num_free(),
             (unsigned)rx_cnt_off, (unsigned)tx_cnt_off);
    // myprintf("ll-dbg,%u,%u\n", (unsigned)rx_cnt_off, (unsigned)tx_cnt_off);
    // myprintf("adv,%u,%u\n");
}

static void *_printer_worker(void *arg)
{
    (void)arg;

    ztimer_sleep(ZTIMER_MSEC, STARTUP_DELAY);

    uint32_t last_wakeup = ztimer_now(ZTIMER_MSEC);
    while (1) {
        ztimer_periodic_wakeup(ZTIMER_MSEC, &last_wakeup, INTERVAL);
        _dump();
        _dump_phy();
        // myprintf("buf%u\n", (unsigned)os_msys_num_free());
        // _dump_conn_offset();
    }

    return NULL;        /* never reached */
}

void llstats_run(void)
{
    memset(llstats, 0, sizeof(llstats));
    memset(&llstats_phy, 0, sizeof(llstats_phy));
    llstats_phy.itvl_start = ztimer_now(ZTIMER_USEC);
    thread_create(_stack, sizeof(_stack),
                  PRIO, THREAD_CREATE_STACKTEST,
                  _printer_worker, NULL, "llstats");
}
