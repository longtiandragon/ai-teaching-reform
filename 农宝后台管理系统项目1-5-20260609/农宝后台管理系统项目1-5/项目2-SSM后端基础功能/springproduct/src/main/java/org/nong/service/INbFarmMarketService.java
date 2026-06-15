package org.nong.service;

import org.nong.common.Result;
import org.nong.entity.NbFarmMarket;
import java.util.Map;

public interface INbFarmMarketService {
    Result<NbFarmMarket> selectList(Map<String, Object> params);
    NbFarmMarket selectById(Integer id);
    int insert(NbFarmMarket market);
    int update(NbFarmMarket market);
    int deleteById(Integer id);
}

