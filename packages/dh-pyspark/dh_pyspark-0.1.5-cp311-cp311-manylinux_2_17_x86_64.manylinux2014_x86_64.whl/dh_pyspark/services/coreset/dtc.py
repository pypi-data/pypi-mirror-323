from typing import Union

from dataheroes.core.coreset.coreset_dtc import CoresetDTC
from dataheroes.data.common import DataParams
from dataheroes.services.common import CoresetParamsDTC, CoresetParams

from dh_pyspark.model.tree_model import SaveOrig
from dh_pyspark.services._coreset_service_base import CoresetTreeServiceBase


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

    def _run_group_pandas_udf(self, df, coreset, coreset_size, class_size, chunk_by_coreset_size_list, max_chunk, scm):
        def _create_coreset_udf(key, pdf):
            return self._udf_create_coreset(key=key, pdf=pdf,
                                            coreset=coreset,
                                            coreset_size=coreset_size,
                                            class_size=class_size,
                                            chunk_by_coreset_size_list=chunk_by_coreset_size_list,
                                            target_column=self._tree_params.target_column,
                                            trace_mode=self._tree_params.trace_mode,
                                            test_udf_log_path=self._tree_params.dhspark_path,
                                            sample_all=self._tree_params.sample_all
            )
        return df.coalesce(max_chunk).groupby(f"chunk_index").applyInPandas(_create_coreset_udf, schema=scm)

