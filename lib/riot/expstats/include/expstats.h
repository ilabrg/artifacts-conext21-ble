
#ifndef EXPSTATS_H
#define EXPSTATS_H

#include <string.h>
#include <limits.h>

#include "net/gnrc/pkt.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    EXPSTATS_APP_TX,
    EXPSTATS_APP_TX_NOBUF,
    EXPSTATS_APP_TX_ERR,
    EXPSTATS_APP_TX_RETRANS,
    EXPSTATS_APP_RX,
    EXPSTATS_APP_ACK,
    EXPSTATS_APP_ACK_ER,
    EXPSTATS_APP_ACK_TO,

    EXPSTATS_ALARM_TX,
    EXPSTATS_ALARM_TX_ERR,
    EXPSTATS_ALRAM_RX,
    EXPSTATS_ALARM_ACK,

    EXPSTATS_NETIF_RX,
    EXPSTATS_NETIF_RX_ERR,
    EXPSTATS_NETIF_RX_PKTBUF_FULL,
    EXPSTATS_NETIF_TX,
    EXPSTATS_NETIF_TX_ER,
    EXPSTATS_NETIF_TX_NOBUF,
    EXPSTATS_NETIF_TX_NC,
    EXPSTATS_NETIF_TX_ABORT,
    EXPSTATS_NETIF_TX_UNSTALLED,
    EXPSTATS_NETIF_TX_MUL,
    EXPSTATS_NETIF_TX_MUL_ER,
    EXPSTATS_NETIF_TX_MUL_NC,
    EXPSTATS_NETIF_TX_MUL_ABORT,
    EXPSTATS_NETIF_TX_MUL_NOBUF,

    EXPSTATS_NIM_CTRL_RXER,
    EXPSTATS_NIM_CTRL_AA_INIT,
    EXPSTATS_NIM_HOST_CREDIT_INIT,
    EXPSTATS_NIM_HOST_CREDIT_SIG,
    EXPSTATS_NIM_HOST_CREDIT_RX_RDY,
    EXPSTATS_NIM_HOST_CREDIT_UPD,
    EXPSTATS_NIM_HOST_CREDIT_TX,
    EXPSTATS_NIM_HOST_CHAN_ALLOC,
    EXPSTATS_NIM_HOST_CHAN_FREE,

    EXPSTATS_RPL_TX,
    EXPSTATS_RPL_TX_DIO,
    EXPSTATS_RPL_TX_DIO_NOBUF,
    EXPSTATS_RPL_TX_DIO_ERR,
    EXPSTATS_RPL_TX_DAO,
    EXPSTATS_RPL_TX_DAO_NOBUF,
    EXPSTATS_RPL_TX_DAO_ACK,
    EXPSTATS_RPL_TX_DAO_ACK_NOBUF,
    EXPSTATS_RPL_TX_DIS,
    EXPSTATS_RPL_TX_DIS_NOBUF,
    EXPSTATS_RPL_TX_DIS_ERR,
    EXPSTATS_RPL_RX,
    EXPSTATS_RPL_RX_ERR,
    EXPSTATS_RPL_RX_DIO,
    EXPSTATS_RPL_RX_DAO,
    EXPSTATS_RPL_RX_DAO_ACK,
    EXPSTATS_RPL_RX_DIS,
    EXPSTATS_RPL_EVT_P_TO,
    EXPSTATS_RPL_EVT_P_STALE,
    EXPSTATS_RPL_EVT_P_SENDDIS,
    EXPSTATS_RPL_EVT_P_REMOVE,
    EXPSTATS_RPL_EVT_DAOTX,
    EXPSTATS_RPL_EVT_INST_CLEANUP,
    EXPSTATS_RPL_EVT_TRICKLE_MSG,

    EXPSTATS_RPBLE_UPDATE_NO_CHANGE,
    EXPSTATS_RPBLE_UPDATE_NEW_CTX,
    EXPSTATS_RPBLE_PARENT_CONN,
    EXPSTATS_RPBLE_CHILD_CONN,
    EXPSTATS_RPBLE_PARENT_LOST,
    EXPSTATS_RPBLE_CHILD_LOST,
    EXPSTATS_RPBLE_PARENT_ABORT,
    EXPSTATS_RPBLE_CHILD_ABORT,

    EXPSTATS_NIB_FT_ADD,
    EXPSTATS_NIB_FT_ADD_DFLT,
    EXPSTATS_NIB_FT_ADD_ERR,
    EXPSTATS_NIB_FT_DEL,
    EXPSTATS_NIB_FT_DEL_DFLT,

    EXPSTATS_IP_SEND_UNI,
    EXPSTATS_IP_DROP,
    EXPSTATS_IP_DMUX,

    EXPSTATS_GNRC_MSG_DROP,

    EXPSTATS_ND_RX_RTR_SOL,
    EXPSTATS_ND_RX_RTR_ADV,
    EXPSATAS_ND_RX_NBR_SOL,
    EXPSTATS_ND_RX_NBR_ADV,
    EXPSTATS_ND_TX_RTR_SOL,
    EXPSTATS_ND_TX_RTR_ADV,
    EXPSTATS_ND_TX_NBR_SOL,
    EXPSTATS_ND_TX_NBR_ADV,

    EXPSTATS_OF_UPDATE,

    EXPSTATS_NUMOF,
};

#define EXPSTATS_TYPE_UDP_REQ           (1U)
#define EXPSTATS_TYPE_UDP_RESP          (2U)
#define EXPSTATS_TYPE_COAP_GET          (3U)
#define EXPSTATS_TYPE_COAP_PUT          (4U)
#define EXPSTATS_TYPE_COAP_OBS          (5U)
#define EXPSTATS_FLAG_FW                (0x80)

#define EXPSTATS_MARKER                 (0xe7e7e7e7)
#define EXPSTATS_MIN_LEN                (10U)

#define EXPSTATS_RPLY_FLAG              (0x80000000)
#define EXPSTATS_SEQ_MASK               (0x00ffffff)
#define EXPSTATS_ID_MASK                (0x7f000000)

#define EXPSTATS_ALL        UINT_MAX

int expstats_init_cmd(int argc, char **argv);

// DEPRECATED
// void expstats_pkt_init(void *buf, size_t buf_len, uint32_t seq, uint8_t id);
// void expstats_seq_set(void *buf, size_t buf_len, uint32_t seq, uint8_t id);
// uint32_t expstats_seq_inc(void *buf, size_t buf_len);
// uint32_t expstats_seq_fmt(uint32_t seq, uint8_t id);


void expstats_mk_pkt(void *buf, size_t buf_len, uint32_t seq, uint16_t paylen);
uint32_t expstats_buf_get_seq(void *buf, size_t buf_len);
uint16_t expstats_buf_get_paylen(void *buf, size_t buf_len);
static inline uint32_t expstats_mk_seq(uint32_t seq, uint8_t id)
{
    return (seq & EXPSTATS_SEQ_MASK) + ((uint32_t)id << 24);
}
static inline unsigned expstats_get_seq(uint32_t seq)
{
    return (seq & EXPSTATS_SEQ_MASK);
}
static inline unsigned expstats_get_id(uint32_t seq)
{
    return (seq & EXPSTATS_ID_MASK) >> 24;
}
static inline int expstats_is_reply(uint32_t seq)
{
    return (seq & EXPSTATS_RPLY_FLAG);
}
static inline uint32_t expstats_inc_seq(uint32_t seq)
{
    return (seq & EXPSTATS_ID_MASK) + expstats_get_seq(seq + 1);
}
static inline uint32_t expstats_mark_reply(uint32_t seq)
{
    return (seq | EXPSTATS_RPLY_FLAG);
}
uint32_t expstats_snip_tx_get_seq(gnrc_pktsnip_t *pkt);

static inline uint32_t expstats_snip_rx_get_seq(gnrc_pktsnip_t *pkt)
{
    return expstats_buf_get_seq(pkt->data, pkt->size);
}


void expstats_log(unsigned stat);
void expstats_log_seq(unsigned stat, uint32_t seq);
void expstats_log_buf(unsigned stat, void *buf, size_t len);
static inline void expstats_log_snip_rx(unsigned stat, gnrc_pktsnip_t *pkt)
{
    expstats_log_buf(stat, pkt->data, pkt->size);
}
static inline void expstats_log_snip_tx(unsigned stat, gnrc_pktsnip_t *pkt)
{
    while (pkt->next != NULL) {
        pkt = pkt->next;
    }
    expstats_log_snip_rx(stat, pkt);
}

void expstats_log_num(unsigned stat, unsigned num);
void expstats_log_ptr(unsigned stat, void *ptr, unsigned num);
void expstats_log_credit(unsigned stat, void *p, uint16_t handle,
                         uint16_t rx, uint16_t tx, uint16_t change);

#ifdef __cplusplus
}
#endif

#endif /* EXPSTATS_H */
/** @} */
