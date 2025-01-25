from typing import Union

from dataheroes.core.coreset.coreset_dtc import CoresetDTC
from dataheroes.data.common import DataParams
from dataheroes.services.common import CoresetParamsDTC, CoresetParams

from dh_pyspark.model.tree_model import SaveOrig
from dh_pyspark.services._coreset_service_base import CoresetTreeServiceBase

import numpy as np
import pyspark.sql.functions as f

class CoresetTreeServiceDTC(CoresetTreeServiceBase):
    coreset_cls = CoresetDTC
    coreset_params_cls = CoresetParamsDTC

    def __init__(self, *, dhspark_path, data_params: Union[DataParams, dict] = None,
                 chunk_size: int = None,
                 chunk_by=None, coreset_size=None,
                 coreset_params: Union[CoresetParams, dict] = CoresetParamsDTC(fair="training",
                                                                               det_weights_behaviour="auto"),
                 n_instances: int = None, n_instances_exact: bool = None,
                 sample_all=None, chunk_sample_ratio=None, class_size=None,
                 save_orig: SaveOrig = SaveOrig.NONE
                 ):
        super().__init__(dhspark_path=dhspark_path, data_params=data_params,
                         chunk_size=chunk_size, chunk_by=chunk_by, coreset_size=coreset_size,
                         coreset_params=coreset_params, sample_all=sample_all,
                         chunk_sample_ratio=chunk_sample_ratio, class_size=class_size,
                         n_instances=n_instances, n_instances_exact=n_instances_exact,
                         save_orig=save_orig)

    def _calculate_coreset_fields(self, df, scm, level, max_chunk, coreset, target_column=None):
        tree_params = self._tree_params
        coreset_size = tree_params.coreset_size

        dhspark_path = tree_params.dhspark_path
        # fair = tree_params.fair
        sample_all = tree_params.sample_all
        class_size = tree_params.class_size
        # deterministic_size = tree_params.deterministic_size
        # in case we use chunk by
        chunk_by_coreset_sizes = None
        if tree_params.chunk_by_tree is not None:
            chunk_by_coreset_sizes = (tree_params.chunk_by_tree[level]["coreset_size"]).to_list()

        if isinstance(coreset_size, dict):
            if class_size is not None:
                raise RuntimeError('It is not allowed to use class_size at the same '
                                   'time as passing class sizes through coreset_size')
            class_size = coreset_size
            coreset_size = None

        elif isinstance(coreset_size, (float, np.floating)) and tree_params.chunk_size is not None:
            coreset_size = int(max(coreset_size * tree_params.chunk_size, 2))

        def _create_coreset_udf(key, pdf):
            return self._udf_create_coreset(key=key, pdf=pdf, coreset=coreset, coreset_size=coreset_size,
                                            target_column=target_column,
                                            trace_mode=tree_params.trace_mode, test_udf_log_path=dhspark_path,
                                            sample_all=sample_all,
                                            class_size=class_size, chunk_by_coreset_size_list=chunk_by_coreset_sizes)

        df = df.coalesce(max_chunk).groupby(f"chunk_index").applyInPandas(_create_coreset_udf, schema=scm)
        df = df.withColumn("level", f.lit(level).cast("int"))
        return df
