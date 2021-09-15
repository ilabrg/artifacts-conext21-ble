
#ifndef LLSTATS_H
#define LLSTATS_H


#include "controller/ble_ll_conn.h"
#include "net/ble.h"

#include "myprint.h"


#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    struct {
        unsigned tx;        /* # of all packets transmitted */
        unsigned ok;        /* # of valid ACKS received */
    } chan[BLE_CHAN_NUMOF];
    uint8_t used;
} llstats_t;

typedef struct {
    uint32_t itvl_start;
    uint32_t rx_start;
    uint32_t tx_start;
    uint32_t rx;
    uint32_t tx;
    uint32_t rx_cnt;
    uint32_t rx_cnt_off;
    uint32_t tx_cnt;
    uint32_t tx_cnt_off;
} llstats_phy_t;

extern llstats_t llstats[MYNEWT_VAL_BLE_MAX_CONNECTIONS];
extern llstats_phy_t llstats_phy;

static inline void llstats_inc_tx(uint16_t conn, uint16_t chan)
{
    /* note: nimble uses connection handles starting from 1 */
    llstats[conn - 1].used = 1;
    llstats[conn - 1].chan[chan].tx++;
}

static inline void llstats_inc_tx_comp(uint16_t conn, uint16_t chan)
{
    /* note: nimble uses connection handles starting from 1 */
    llstats[conn - 1].used = 1;
    llstats[conn - 1].chan[chan].ok++;
}

void llstats_run(void);

static inline void llstats_dump_conn_tim(struct ble_ll_conn_sm *connsm, unsigned resched)
{
    myprintf("ll%u,%u(%u)\n",
             (unsigned)connsm->conn_handle,
             (unsigned)connsm->anchor_point, resched);
}

static inline void llstats_dump_slave_latency(struct ble_ll_conn_sm *connsm, uint16_t latency)
{
    myprintf("ll%u,sl%u,is%u\n",
             (unsigned)connsm->conn_handle,
             (unsigned)connsm->slave_latency,
             (unsigned)latency);
}

static inline void llstats_rxon(void)
{
    llstats_phy.rx_start = ztimer_now(ZTIMER_USEC);
    ++llstats_phy.rx_cnt;
}

static inline void llstats_rxoff(void)
{
    llstats_phy.rx += (ztimer_now(ZTIMER_USEC) - llstats_phy.rx_start);
    ++llstats_phy.rx_cnt_off;
}

static inline void llstats_txon(void)
{
    llstats_phy.tx_start = ztimer_now(ZTIMER_USEC);
    ++llstats_phy.tx_cnt;
}

static inline void llstats_txoff(void)
{
    llstats_phy.tx += (ztimer_now(ZTIMER_USEC) - llstats_phy.tx_start);
    ++llstats_phy.tx_cnt_off;
}

#ifdef __cplusplus
}
#endif

#endif /* LLSTATS_H */
/** @} */
