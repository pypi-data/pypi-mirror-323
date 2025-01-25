#pragma once
#include <string>
#include <vector>

#include "hardware_ident.h"
#include "hardware_type.h"
#include "infra/system.h"

namespace akida::np {

constexpr bool is_cnp(hw::Type type) {
  return type == hw::Type::CNP1 || type == hw::Type::CNP2;
}

constexpr bool is_fnp(hw::Type type) {
  return type == hw::Type::FNP2 || type == hw::Type::FNP3;
}

struct Info {
  // TODO: can be replaced by default Three-way comparison in C++20
  bool operator==(const Info& other) const {
    return ident == other.ident && types == other.types;
  }
  // TODO: can be replaced by default Three-way comparison in C++20
  bool operator!=(const Info& other) const { return !(*this == other); }
  hw::Ident ident;
  hw::Types types;
};

/**
 * The layout of a mesh of Neural Processors
 */
struct Mesh final {
  // TODO: can be replaced by default Three-way comparison in C++20
  bool operator==(const Mesh& other) const {
    return dma_event == other.dma_event && dma_conf == other.dma_conf &&
           nps == other.nps && skip_dmas == other.skip_dmas;
  }
  // TODO: can be replaced by default Three-way comparison in C++20
  bool operator!=(const Mesh& other) const { return !(*this == other); }

  hw::Ident dma_event{};         /**<The DMA event endpoint */
  hw::Ident dma_conf{};          /**<The DMA configuration endpoint */
  std::vector<Info> nps{};       /**<The available Neural Processors */
  std::vector<Info> skip_dmas{}; /**<The available skip dmas */
};

}  // namespace akida::np
