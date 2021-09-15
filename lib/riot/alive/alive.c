

#include "random.h"
#include "thread.h"
#include "ztimer.h"
#include "alive.h"
#include "myprint.h"

#define MYADDR      0
#if MYADDR
#include "net/bluetil/addr.h"
#include "host/ble_hs.h"
#include "nimble_riot.h"
#endif

#define ALIVE_PRIO          (THREAD_PRIORITY_MAIN + 4)
static char _alive_stack[THREAD_STACKSIZE_DEFAULT];

#define STARTUP_DELAY       (15 * 1000)
#define ITVL_MS             (ALIVE_ITVL * 1000)

static void *_alive_thread(void *arg)
{
    (void)arg;
    unsigned cnt = 0;
#if MYADDR
    char myaddr[BLUETIL_ADDR_STRLEN];
#endif

    /* add a randomized startup delay to prevent STDIO cluttering */
    ztimer_sleep(ZTIMER_MSEC, random_uint32_range(STARTUP_DELAY,
                                                  (STARTUP_DELAY + ITVL_MS)));

    while (1) {
#if MYADDR
        uint8_t addr[BLE_ADDR_LEN];
        uint8_t addrn[BLE_ADDR_LEN];
        ble_hs_id_copy_addr(nimble_riot_own_addr_type, addr, NULL);
        bluetil_addr_swapped_cp(addr, addrn);
        bluetil_addr_sprint(myaddr, addrn);
        myprintf("ALIVE-%u %s\n", cnt++, myaddr);
#else
        myprintf("ALIVE-%u\n", cnt++);
#endif

        ztimer_sleep(ZTIMER_MSEC, ITVL_MS);
    }
    return NULL;
}

void alive_run(void)
{
    thread_create(_alive_stack, sizeof(_alive_stack),
                  ALIVE_PRIO, THREAD_CREATE_STACKTEST,
                  _alive_thread, NULL, "alive");
}
