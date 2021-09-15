

#include "fmt.h"
#include "myprint.h"

#include "net/bluetil/addr.h"

#include "bledump.h"



static void _addr_sprint(char *out, const uint8_t *addr)
{
    assert(out);
    assert(addr);

    fmt_byte_hex(out, addr[0]);
    for (unsigned i = 1; i < BLE_ADDR_LEN; i++) {
        out += 2;
        *out++ = ':';
        fmt_byte_hex(out, addr[i]);
    }
    out += 2;
    *out = '\0';
}

static void _addr_print(const uint8_t *addr)
{
    assert(addr);

    char str[BLUETIL_ADDR_STRLEN];
    _addr_sprint(str, addr);
    myprintf("%s", str);
}

static void _log_evt(const char *msg, int slot, const uint8_t *addr)
{
    myprintf("ble: %s (%i|", msg, slot);
    if (addr) {
        _addr_print(addr);
    } else {
        myprintf("n/a");
    }
    myputs(")");
}

void bledump_on_evt(int slot, nimble_netif_event_t type, const uint8_t *addr)
{
    switch (type) {
        case NIMBLE_NETIF_ACCEPTING:
            _log_evt("adv_start", slot, addr);
            break;
        case NIMBLE_NETIF_ACCEPT_STOP:
            _log_evt("adv_stop", slot, addr);
            break;
        case NIMBLE_NETIF_INIT_MASTER:
            _log_evt("init_m", slot, addr);
            break;
        case NIMBLE_NETIF_INIT_SLAVE:
            _log_evt("init_s", slot, addr);
            break;
        case NIMBLE_NETIF_CONNECTED_MASTER:
            _log_evt("conn_m", slot, addr);
            break;
        case NIMBLE_NETIF_CONNECTED_SLAVE:
            _log_evt("conn_s", slot, addr);
            break;
        case NIMBLE_NETIF_CLOSED_MASTER:
            _log_evt("close_m", slot, addr);
            break;
        case NIMBLE_NETIF_CLOSED_SLAVE:
            _log_evt("close_s", slot, addr);
            break;
        case NIMBLE_NETIF_ABORT_MASTER:
            _log_evt("abort_m", slot, addr);
            break;
        case NIMBLE_NETIF_ABORT_SLAVE:
            _log_evt("abort_s", slot, addr);
            break;
        case NIMBLE_NETIF_CONN_UPDATED:
            _log_evt("update", slot, addr);
            break;
        default:
            myprintf("error: unkown event: %i\n", (int)type);
            assert(0);
            return;
    }
}
