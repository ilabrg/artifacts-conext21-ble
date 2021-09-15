
#ifndef BLEDUMP_H
#define BLEDUMP_H

#ifdef __cplusplus
extern "C" {
#endif

#include "nimble_netif.h"

void bledump_on_evt(int slot, nimble_netif_event_t type, const uint8_t *addr);

#ifdef __cplusplus
}
#endif

#endif /* BLEDUMP_H */
/** @} */
