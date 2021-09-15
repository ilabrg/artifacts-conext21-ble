/*
 * Copyright (C) 2020,2021 Freie Universität Berlin
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

/**
 * @ingroup     exp_coapexp
 * @{
 *
 * @file
 * @brief       exp Coap Exp
 *
 * @author      Hauke Petersen <hauke.petersen@fu-berlin.de>
 *
 * @}
 */

#include "nimble_statconn.h"

#include "myprint.h"
#if IS_USED(MODULE_ALIVE)
#include "alive.h"
#endif
#include "bledump.h"
#include "coapexp.h"
#ifdef MODULE_LLSTATS
#include "llstats.h"
#endif


int main(void)
{
    myputs(APPNAME);

    nimble_statconn_eventcb(bledump_on_evt);
#if IS_USED(MODULE_ALIVE)
    alive_run();
#endif
#ifdef MODULE_LLSTATS
    llstats_run();
#endif
    coapexp_run();

    return 0;
}
