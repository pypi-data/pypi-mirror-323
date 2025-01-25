#pragma once
#include <cstdint>
#include "akida/np.h"
#include "dma_engine.h"
#include "external_mem_mgr.h"
#include "memory_mgr.h"
namespace akida::skipdma {
// allocate memory for descriptors
void program_store_channel_desc_buff_addr(
    dma::addr skipdma_descriptor_base_addr, const dma::Config& dma_config,
    const ProgramInfo::SkipDmaInfoTrack& skipdma,
    ExternalMemoryMgr* ext_mem_mgr, HardwareDriver* driver);
void program_load_channel_desc_buff_addr(
    dma::addr skipdma_descriptor_base_addr, const dma::Config& dma_config,
    const ProgramInfo::SkipDmaInfoTrack& skipdma,
    ExternalMemoryMgr* ext_mem_mgr, HardwareDriver* driver);
// allocate memory for outbound
dma::addr program_store_channel_ob_buff_addr(
    const uint8_t max_outbound, const dma::Config& dma_config,
    const ProgramInfo::SkipDmaInfoTrack& skipdma, MemoryMgr* mem_mgr,
    ExternalMemoryMgr* ext_mem_mgr, HardwareDriver* driver);
// Enable OB buffer clear mode
void store_channel_enable_pld_clr(const dma::Config& dma_config,
                                  const ProgramInfo::SkipDmaInfoTrack& skipdma,
                                  MemoryMgr* mem_mgr,
                                  ExternalMemoryMgr* ext_mem_mgr,
                                  HardwareDriver* driver);
// program descriptors container size
uint8_t program_store_channel_cont_size(
    const dma::Config& dma_config, const ProgramInfo::SkipDmaInfoTrack& skipdma,
    MemoryMgr* mem_mgr, ExternalMemoryMgr* ext_mem_mgr, HardwareDriver* driver,
    const bool is_pipeline, const size_t batch_size);
void program_load_channel_cont_size(
    const dma::Config& dma_config, const ProgramInfo::SkipDmaInfoTrack& skipdma,
    MemoryMgr* mem_mgr, ExternalMemoryMgr* ext_mem_mgr, HardwareDriver* driver,
    const uint8_t cont_size);
}  // namespace akida::skipdma
