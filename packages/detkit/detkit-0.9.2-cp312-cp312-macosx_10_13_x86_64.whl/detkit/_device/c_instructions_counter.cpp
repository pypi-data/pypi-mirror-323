/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


// =======
// Headers
// =======

#include "./c_instructions_counter.h"
#include <string.h>
#include <iostream>

#if __linux__
    #include <asm/unistd.h>
    #include <sys/ioctl.h>
    #include <unistd.h>
    #include <inttypes.h>
    #include <sys/types.h>
#endif


// ===============
// perf event open
// ===============

#if __linux__
    static long perf_event_open(
            struct perf_event_attr* hw_event,
            pid_t pid,
            int cpu,
            int group_fd,
            unsigned long flags)
    {
        int ret;
        ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd,
                      flags);
        return ret;
    }
#endif


// ===========
// Constructor
// ===========

cInstructionsCounter::cInstructionsCounter():
    fd(-1),
    count(0),
    inst_per_flop(1.0)
{
    #if __linux__
        memset(&this->pe, 0, sizeof(struct perf_event_attr));
        this->pe.size = sizeof(struct perf_event_attr);
        this->pe.disabled = 1;
        this->pe.exclude_kernel = 1;
        this->pe.exclude_hv = 1;  // Don't count hypervisor events.
        
        // Option 1: Count "pre-defined" hardware instructions
        // This option measures all CPU operations, including floating point,
        // memory, etc. This is has more noise as the count is not solely the
        // floating point count.
        this->pe.type = PERF_TYPE_HARDWARE;
        this->pe.config = PERF_COUNT_HW_INSTRUCTIONS;

        // Option 2: count raw instructions specifically for floating point.
        // This option measures only floating point operations, not other tasks
        // such as memory operations. This option gives me zero counts on a few
        // CPUs I tested, as it seems it is not supported, so I use option 1
        // above for now.
        // this->pe.type = PERF_TYPE_RAW;  // Use raw events
        // this->pe.config = 0xC7;         // FP instructions
        // this->pe.config1 = 0x4;        // Unit mask (based on CPU)
            
        this->fd = perf_event_open(&this->pe, 0, -1, -1, 0);
        if (this->fd == -1)
        {
            // Error, cannot open the leader.
            this->count = -1;
        }
    #endif
}


// ==========
// Destructor
// ==========

cInstructionsCounter::~cInstructionsCounter()
{
    #if __linux__
        if (this->fd != -1)
        {
            close(this->fd);
        }
    #endif
}


// =================
// set inst per flop
// =================

void cInstructionsCounter::set_inst_per_flop(double inst_per_flop)
{
    this->inst_per_flop = inst_per_flop;
}


// =====
// Start
// =====

void cInstructionsCounter::start()
{
    #if __linux__
        if (this->fd != -1)
        {
            ioctl(this->fd, PERF_EVENT_IOC_RESET, 0);
            ioctl(this->fd, PERF_EVENT_IOC_ENABLE, 0);
        }
    #endif
}


// ====
// Stop
// ====

void cInstructionsCounter::stop()
{
    #if __linux__
        
        long long current_count;

        if (this->fd != -1)
        {
            ioctl(this->fd, PERF_EVENT_IOC_DISABLE, 0);
            ssize_t bytes = read(this->fd, &current_count,
                                 sizeof(long long));
            if (bytes < 0)
            {
                std::cerr << "Error reading file." << std::endl;
            }

            // Accumulate counts
            this->count += current_count;
        }
    #endif
}


// =====
// reset
// =====

void cInstructionsCounter::reset()
{
    this->count = 0;
}


// =========
// get count
// =========

long long cInstructionsCounter::get_count()
{
    return this->count;
}


// =========
// get flops
// =========

long long cInstructionsCounter::get_flops()
{
    return static_cast<long long>(this->count / this->inst_per_flop);
}
