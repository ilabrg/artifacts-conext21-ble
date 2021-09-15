
#include <string.h>

#include "expstats.h"

#ifdef MODULE_MYPRINT
#include "myprint.h"
#endif

#define POS_MARKER          (4U)
#define POS_SEQ             (8U)
#define POS_PAYLEN          (10U)

static const uint32_t _marker = EXPSTATS_MARKER;

#ifdef MODULE_MYPRINT
static const char *_names[] = {
    [EXPSTATS_APP_TX] =                 "A_TX",
    [EXPSTATS_APP_TX_NOBUF] =           "A_TX_F",
    [EXPSTATS_APP_TX_ERR] =             "A_TX_ER",
    [EXPSTATS_APP_TX_RETRANS] =         "A_TX_RE",
    [EXPSTATS_APP_RX] =                 "A_RX",
    [EXPSTATS_APP_ACK] =                "A_ACK",
    [EXPSTATS_APP_ACK_ER] =             "A_ACK_ER",
    [EXPSTATS_APP_ACK_TO] =             "A_ACK_TO",

    [EXPSTATS_ALARM_TX] =               "AL_TX",
    [EXPSTATS_ALARM_TX_ERR] =           "AL_TX_ER",
    [EXPSTATS_ALRAM_RX] =               "AL_RX",
    [EXPSTATS_ALARM_ACK] =              "AL_ACK",

    [EXPSTATS_NETIF_RX] =               "N_RX",
    [EXPSTATS_NETIF_RX_ERR] =           "N_RX_ER",
    [EXPSTATS_NETIF_RX_PKTBUF_FULL] =   "N_RX_NPB",
    [EXPSTATS_NETIF_TX] =               "N_TX",
    [EXPSTATS_NETIF_TX_ER] =            "N_TX_ER",
    [EXPSTATS_NETIF_TX_NOBUF] =         "N_TX_NNB",
    [EXPSTATS_NETIF_TX_NC] =            "N_TX_NC",
    [EXPSTATS_NETIF_TX_ABORT] =         "N_TX_A",
    [EXPSTATS_NETIF_TX_UNSTALLED] =     "N_TX_US",
    [EXPSTATS_NETIF_TX_MUL] =           "N_TX_M",
    [EXPSTATS_NETIF_TX_MUL_ER] =        "N_TX_M_ER",
    [EXPSTATS_NETIF_TX_MUL_NOBUF] =     "N_TX_M_NNB",
    [EXPSTATS_NETIF_TX_MUL_NC] =        "N_TX_M_NC",
    [EXPSTATS_NETIF_TX_MUL_ABORT] =     "N_TX_M_A",

    [EXPSTATS_NIM_CTRL_RXER] =          "C_RXER",
    [EXPSTATS_NIM_CTRL_AA_INIT] =       "C_AA",
    [EXPSTATS_NIM_HOST_CREDIT_INIT] =   "H_CI",
    [EXPSTATS_NIM_HOST_CREDIT_SIG] =    "H_CS",
    [EXPSTATS_NIM_HOST_CREDIT_RX_RDY] = "H_CRR",
    [EXPSTATS_NIM_HOST_CREDIT_UPD] =    "H_CU",
    [EXPSTATS_NIM_HOST_CREDIT_TX] =     "H_CTX",
    [EXPSTATS_NIM_HOST_CHAN_ALLOC] =    "H_CHA",
    [EXPSTATS_NIM_HOST_CHAN_FREE] =     "H_CHF",

    [EXPSTATS_RPL_TX] =                 "R_TX",
    [EXPSTATS_RPL_TX_DIO] =             "R_TX_DIO",
    [EXPSTATS_RPL_TX_DIO_NOBUF] =       "R_TX_DIO_NB",
    [EXPSTATS_RPL_TX_DIO_ERR] =         "R_TX_DIO_ER",
    [EXPSTATS_RPL_TX_DAO] =             "R_TX_DAO",
    [EXPSTATS_RPL_TX_DAO_NOBUF] =       "R_TX_DAONB",
    [EXPSTATS_RPL_TX_DAO_ACK] =         "R_TX_DAO_ACK",
    [EXPSTATS_RPL_TX_DAO_ACK_NOBUF] =   "R_TX_DAO_ACKNB",
    [EXPSTATS_RPL_TX_DIS] =             "R_TX_DIS",
    [EXPSTATS_RPL_TX_DIS_NOBUF] =       "R_TX_DISNB",
    [EXPSTATS_RPL_TX_DIS_ERR] =         "R_TX_DISER",
    [EXPSTATS_RPL_RX] =                 "R_RX",
    [EXPSTATS_RPL_RX_ERR] =             "R_RX_ER",
    [EXPSTATS_RPL_RX_DIO] =             "R_RX_DIO",
    [EXPSTATS_RPL_RX_DAO] =             "R_RX_DAO",
    [EXPSTATS_RPL_RX_DAO_ACK] =         "R_RX_DAO_ACK",
    [EXPSTATS_RPL_RX_DIS] =             "R_RX_DIS",
    [EXPSTATS_RPL_EVT_P_TO] =           "R_E_PTO",
    [EXPSTATS_RPL_EVT_P_STALE] =        "R_E_PS",
    [EXPSTATS_RPL_EVT_P_SENDDIS] =      "R_E_PDIS",
    [EXPSTATS_RPL_EVT_P_REMOVE] =       "R_E_PR",
    [EXPSTATS_RPL_EVT_DAOTX] =          "R_E_DAOTX",
    [EXPSTATS_RPL_EVT_INST_CLEANUP] =   "R_E_IC",
    [EXPSTATS_RPL_EVT_TRICKLE_MSG] =    "R_E_T",

    [EXPSTATS_RPBLE_UPDATE_NO_CHANGE] = "B_UNC",
    [EXPSTATS_RPBLE_UPDATE_NEW_CTX] =   "B_CTX",
    [EXPSTATS_RPBLE_PARENT_CONN] =      "B_PC",
    [EXPSTATS_RPBLE_CHILD_CONN] =       "B_CC",
    [EXPSTATS_RPBLE_PARENT_LOST] =      "B_PL",
    [EXPSTATS_RPBLE_CHILD_LOST] =       "B_CL",
    [EXPSTATS_RPBLE_PARENT_ABORT] =     "B_PA",
    [EXPSTATS_RPBLE_CHILD_ABORT] =      "B_CA",

    [EXPSTATS_NIB_FT_ADD]               "F_A",
    [EXPSTATS_NIB_FT_ADD_DFLT]          "F_AD",
    [EXPSTATS_NIB_FT_ADD_ERR]           "F_AE",
    [EXPSTATS_NIB_FT_DEL]               "F_D",
    [EXPSTATS_NIB_FT_DEL_DFLT]          "F_DD",

    [EXPSTATS_IP_SEND_UNI]              "I_U",
    [EXPSTATS_IP_DROP]                  "I_D",
    [EXPSTATS_IP_DMUX]                  "I_MUX",

    [EXPSTATS_GNRC_MSG_DROP]            "G_MD",

    [EXPSTATS_ND_RX_RTR_SOL]            "ND_RX_RS",
    [EXPSTATS_ND_RX_RTR_ADV]            "ND_RX_RA",
    [EXPSATAS_ND_RX_NBR_SOL]            "ND_RX_NS",
    [EXPSTATS_ND_RX_NBR_ADV]            "ND_RX_NA",
    [EXPSTATS_ND_TX_RTR_SOL]            "ND_TX_RS",
    [EXPSTATS_ND_TX_RTR_ADV]            "ND_TX_RA",
    [EXPSTATS_ND_TX_NBR_SOL]            "ND_TX_NS",
    [EXPSTATS_ND_TX_NBR_ADV]            "ND_TX_NA",

    [EXPSTATS_OF_UPDATE]                "OF",

    [EXPSTATS_NUMOF] =                  "NUMOF",
};
#endif

static int _isdata(uint8_t *data, size_t len)
{
    return ((len >= EXPSTATS_MIN_LEN) &&
            (memcmp(&data[len - POS_MARKER], &_marker, sizeof(uint32_t)) == 0));
}

void expstats_mk_pkt(void *buf, size_t buf_len, uint32_t seq, uint16_t paylen)
{
    uint8_t *data = (uint8_t *)buf;
    memcpy(&data[buf_len - POS_MARKER], &_marker, sizeof(uint32_t));
    memcpy(&data[buf_len - POS_SEQ], &seq, sizeof(uint32_t));
    memcpy(&data[buf_len - POS_PAYLEN], &paylen, sizeof(uint16_t));
}
uint32_t expstats_buf_get_seq(void *buf, size_t buf_len)
{
    uint8_t *data = (uint8_t *)buf;
    uint32_t seq;
    memcpy(&seq, &data[buf_len - POS_SEQ], sizeof(uint32_t));
    return seq;
}

uint32_t expstats_snip_tx_get_seq(gnrc_pktsnip_t *pkt)
{
    while (pkt->next != NULL) {
        pkt = pkt->next;
    }
    if (_isdata((uint8_t *)pkt->data, pkt->size)) {
        return expstats_buf_get_seq(pkt->data, pkt->size);
    }
    else {
        return 0;
    }
}

uint16_t expstats_buf_get_paylen(void *buf, size_t buf_len)
{
    uint8_t *data = (uint8_t *)buf;
    uint16_t len;
    memcpy(&len, &data[buf_len - POS_PAYLEN], sizeof(uint16_t));
    return len;
}

void expstats_log(unsigned stat)
{
#ifdef MODULE_MYPRINT
    myprintf("~%s\n", _names[stat]);
#else
    (void)stat;
#endif
}

void expstats_log_seq(unsigned stat, uint32_t seq)
{
#ifdef MODULE_MYPRINT
    char dir = (expstats_is_reply(seq)) ? '<' : '>';
    myprintf("~%s:%u%c%u\n", _names[stat],
             expstats_get_id(seq), dir, expstats_get_seq(seq));
#else
    (void)stat;
    (void)seq;
#endif
}

void expstats_log_buf(unsigned stat, void *buf, size_t len)
{
    uint8_t *data = (uint8_t *)buf;
    if (_isdata(data, len)) {
        expstats_log_seq(stat, expstats_buf_get_seq(data, len));
    }
    else {
        expstats_log(stat);
    }
}

void expstats_log_num(unsigned stat, unsigned num)
{
#ifdef MODULE_MYPRINT
    myprintf("~%s:%u\n", _names[stat], num);
#else
    (void)stat;
    (void)num;
#endif
}

void expstats_log_ptr(unsigned stat, void *ptr, unsigned num)
{
#ifdef MODULE_MYPRINT
    myprintf("~%s:%p;%u\n", _names[stat], ptr, num);
#else
    (void)stat;
    (void)ptr;
    (void)num;
#endif
}

void expstats_log_credit(unsigned stat, void *p, uint16_t handle,
                         uint16_t rx, uint16_t tx, uint16_t change)
{
#ifdef MODULE_MYPRINT
    myprintf("~%s:%p;%i;%i;%i;%i\n", _names[stat], p, (int)handle,
             (int)rx, (int)tx, (int)change);
#else
    (void)stat;
    (void)p;
    (void)handle;
    (void)rx;
    (void)tx;
    (void)change;
#endif
}
