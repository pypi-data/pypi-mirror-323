#include <torch/all.h>

#include "core/registration.h"

#include "ops.h"

// Note on op signatures:
// The X_meta signatures are for the meta functions corresponding to op X.
// They must be kept in sync with the signature for X. Generally, only
// functions that return Tensors require a meta function.
//
// See the following links for detailed docs on op registration and function
// schemas.
// https://docs.google.com/document/d/1_W62p8WJOQQUzPsJYa7s701JXt0qf2OfLub2sbkHOaU/edit#heading=h.ptttacy8y1u9
// https://github.com/pytorch/pytorch/blob/main/aten/src/ATen/native/README.md#annotations

TORCH_LIBRARY_EXPAND(TORCH_EXTENSION_NAME, ops) {
  // Attention ops
  // Compute the attention between an input query and the cached
  // keys/values using PagedAttention.
  ops.def(
      "paged_attention_v1("
      "    Tensor! out, Tensor query, Tensor key_cache,"
      "    Tensor value_cache, int num_kv_heads, float scale,"
      "    Tensor block_tables, Tensor seq_lens, int block_size,"
      "    int max_seq_len, Tensor? alibi_slopes,"
      "    str kv_cache_dtype, float k_scale, float v_scale,"
      "    int tp_rank, int blocksparse_local_blocks,"
      "    int blocksparse_vert_stride, int blocksparse_block_size,"
      "    int blocksparse_head_sliding_step) -> ()");
  ops.impl("paged_attention_v1", torch::kCUDA, &paged_attention_v1);

  // PagedAttention V2.
  ops.def(
      "paged_attention_v2("
      "    Tensor! out, Tensor! exp_sums, Tensor! max_logits,"
      "    Tensor! tmp_out, Tensor query, Tensor key_cache,"
      "    Tensor value_cache, int num_kv_heads, float scale,"
      "    Tensor block_tables, Tensor seq_lens, int block_size,"
      "    int max_seq_len, Tensor? alibi_slopes,"
      "    str kv_cache_dtype, float k_scale, float v_scale,"
      "    int tp_rank, int blocksparse_local_blocks,"
      "    int blocksparse_vert_stride, int blocksparse_block_size,"
      "    int blocksparse_head_sliding_step) -> ()");
  ops.impl("paged_attention_v2", torch::kCUDA, &paged_attention_v2);

  // Reshape the key and value tensors and cache them.
  ops.def(
      "reshape_and_cache(Tensor key, Tensor value,"
      "                  Tensor! key_cache, Tensor! value_cache,"
      "                  Tensor slot_mapping,"
      "                  str kv_cache_dtype,"
      "                  float k_scale, float v_scale) -> ()");
  ops.impl("reshape_and_cache", torch::kCUDA, &reshape_and_cache);
}

REGISTER_EXTENSION(TORCH_EXTENSION_NAME)
