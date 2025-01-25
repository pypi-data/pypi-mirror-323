#include "skipdma_ops.h"

#include <cstddef>
#include "akida/registers_top_level.h"
#include "dma_config_mem_rw.h"
#include "engine/dma_config_ops.h"
#include "engine/registers_skipdma.h"

namespace akida::skipdma {

static dma::w32 read_reg(const hw::Ident& skipmda_id, const uint16_t dest_addr,
                         const dma::Config& dma_config, MemoryMgr* mem_mgr,
                         HardwareDriver* driver) {
  // read the size of ob (config dma data file format)
  dma::w32 header[dma::kConfigNpHeaderWordSize]{0};
  dma::format_config_header(&header[0], skipmda_id,
                            dma::Target::SkipDmaRegisters, 1, dest_addr, false);
  // returned value
  dma::w32 reg{};
  // read register
  dma::dma_config_read(&reg, 1, &header[0], dma_config, mem_mgr, driver);
  return reg;
}

static void write_reg(const dma::w32 value, const hw::Ident& skipmda_id,
                      const uint16_t dest_addr, const dma::Config& dma_config,
                      ExternalMemoryMgr* ext_mem_mgr, HardwareDriver* driver) {
  // config dma configuration data file
  constexpr uint8_t payload_size = 1U;
  constexpr uint8_t buff_size = dma::kConfigNpHeaderWordSize + payload_size;
  dma::w32 buffer[buff_size]{0};
  auto& header = buffer[0];
  auto& payload = buffer[buff_size - 1];
  payload = value;
  dma::format_config_header(&header, skipmda_id, dma::Target::SkipDmaRegisters,
                            payload_size, dest_addr, false);
  dma::dma_config_write(&buffer[0], buff_size, dma_config, ext_mem_mgr, driver);
}

uint8_t program_store_channel_cont_size(
    const dma::Config& dma_config, const ProgramInfo::SkipDmaInfoTrack& skipdma,
    MemoryMgr* mem_mgr, ExternalMemoryMgr* ext_mem_mgr, HardwareDriver* driver,
    const bool is_pipeline, const size_t batch_size) {
  const auto id = skipdma.info.ident;
  const auto channel_idx = skipdma.info.ident.channel_idx;
  const auto skip_length = skipdma.skip_length;
  // write Replay Maximum Outbound (store channel)
  // TODO: This value is set according to the documentation
  // Akida_skipdma_spec_v3p1.docx. It should also consider wether there is
  // partial reconfiguration or not. For now, partial reconfiguration with skip
  // connection is forbidden. This code need to be updated when partial
  // reconfiguration will be implemented.
  uint8_t max_outbound{2};
  if (is_pipeline) {
    max_outbound = static_cast<uint8_t>(
        std::min(static_cast<size_t>(skip_length + 3), batch_size + 1));
  }
  auto dest_addr =
      static_cast<uint16_t>(skipdma::REPLAY_MAX_OB_DESC_BUFF_REG(channel_idx));
  auto reg = read_reg(id, dest_addr, dma_config, mem_mgr, driver);
  set_field(&reg, skipdma::MAX_OB_DESC_BUFF, max_outbound);
  write_reg(reg, id, dest_addr, dma_config, ext_mem_mgr, driver);
  return max_outbound;
}

void program_load_channel_cont_size(
    const dma::Config& dma_config, const ProgramInfo::SkipDmaInfoTrack& skipdma,
    MemoryMgr* mem_mgr, ExternalMemoryMgr* ext_mem_mgr, HardwareDriver* driver,
    const uint8_t cont_size) {
  const auto id = skipdma.info.ident;
  const auto channel_idx = skipdma.info.ident.channel_idx;
  // write Container Size Register (load channel)
  const auto dest_addr =
      static_cast<uint16_t>(skipdma::CONT_SIZE_REG(channel_idx));
  auto reg = read_reg(id, dest_addr, dma_config, mem_mgr, driver);
  set_field(&reg, skipdma::MAX_DESC_CONT, cont_size - 1);
  write_reg(reg, id, dest_addr, dma_config, ext_mem_mgr, driver);
}

void program_store_channel_desc_buff_addr(
    dma::addr skipdma_descriptor_base_addr, const dma::Config& dma_config,
    const ProgramInfo::SkipDmaInfoTrack& skipdma,
    ExternalMemoryMgr* ext_mem_mgr, HardwareDriver* driver) {
  const auto id = skipdma.info.ident;
  const auto channel_idx = skipdma.info.ident.channel_idx;
  // Replay OB Event Buffer Address Register (store channel)
  auto dest_addr =
      static_cast<uint16_t>(skipdma::REPLAY_DESC_BUFF_ADDR_REG(channel_idx));
  write_reg(skipdma_descriptor_base_addr, id, dest_addr, dma_config,
            ext_mem_mgr, driver);
}

void program_load_channel_desc_buff_addr(
    dma::addr skipdma_descriptor_base_addr, const dma::Config& dma_config,
    const ProgramInfo::SkipDmaInfoTrack& skipdma,
    ExternalMemoryMgr* ext_mem_mgr, HardwareDriver* driver) {
  const auto id = skipdma.info.ident;
  const auto channel_idx = skipdma.info.ident.channel_idx;
  // Container Address Register (load channel)
  const auto dest_addr =
      static_cast<uint16_t>(skipdma::CONT_ADDR_REG(channel_idx));
  write_reg(skipdma_descriptor_base_addr, id, dest_addr, dma_config,
            ext_mem_mgr, driver);
}

dma::addr program_store_channel_ob_buff_addr(
    const uint8_t max_outbound, const dma::Config& dma_config,
    const ProgramInfo::SkipDmaInfoTrack& skipdma, MemoryMgr* mem_mgr,
    ExternalMemoryMgr* ext_mem_mgr, HardwareDriver* driver) {
  // read the size of ob (config dma data file format)
  const auto id = skipdma.info.ident;
  const auto channel_idx = skipdma.info.ident.channel_idx;
  auto dest_addr =
      static_cast<uint16_t>(skipdma::DMA_OB_PLD_CLR_REG(channel_idx));
  auto reg = read_reg(id, dest_addr, dma_config, mem_mgr, driver);
  //  set ob byte size. In register the size is in 32-bit, it should be multiply
  //  by 4, to get the size in 8-bit
  constexpr uint32_t header_size = 8;
  const auto ob_size =
      (get_field(reg, skipdma::OB_PLD_CLR_SIZE) + header_size) * 4;
  // TODO: this memory should be free when unprogram
  size_t ob_mem_size = static_cast<size_t>(ob_size) * max_outbound;
  auto ob_mem = mem_mgr->alloc(ob_mem_size);
  // now write ob memory address in skip dma register (store channel)
  dest_addr = static_cast<uint16_t>(
      skipdma::REPLAY_OB_EVENT_BUFF_ADDR_REG(channel_idx));
  write_reg(ob_mem, id, dest_addr, dma_config, ext_mem_mgr, driver);
  return ob_mem;
}
void store_channel_enable_pld_clr(const dma::Config& dma_config,
                                  const ProgramInfo::SkipDmaInfoTrack& skipdma,
                                  MemoryMgr* mem_mgr,
                                  ExternalMemoryMgr* ext_mem_mgr,
                                  HardwareDriver* driver) {
  // read ob pld clear size register
  const auto id = skipdma.info.ident;
  const auto channel_idx = skipdma.info.ident.channel_idx;
  auto dest_addr =
      static_cast<uint16_t>(skipdma::DMA_OB_PLD_CLR_REG(channel_idx));
  auto reg = read_reg(id, dest_addr, dma_config, mem_mgr, driver);
  // enable pld clear
  set_field(&reg, skipdma::OB_PLD_CLR_EN, 1);
  write_reg(reg, id, dest_addr, dma_config, ext_mem_mgr, driver);
}
}  // namespace akida::skipdma
