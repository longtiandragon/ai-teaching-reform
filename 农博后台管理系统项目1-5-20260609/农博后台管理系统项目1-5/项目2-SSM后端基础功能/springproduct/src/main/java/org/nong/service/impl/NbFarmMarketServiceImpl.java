package org.nong.service.impl;

import org.nong.common.Result;
import org.nong.entity.NbFarmMarket;
import org.nong.mapper.NbFarmMarketMapper;
import org.nong.service.INbFarmMarketService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;

@Service
public class NbFarmMarketServiceImpl implements INbFarmMarketService {
    
    @Autowired
    private NbFarmMarketMapper marketMapper;
    
    @Override
    @SuppressWarnings("unchecked")
    public Result<NbFarmMarket> selectList(Map<String, Object> params) {
        List<NbFarmMarket> list = marketMapper.selectList(params);
        Long total = marketMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);
        result.setTotal(total);
        result.buildPageData();
        return result;
    }
    
    @Override
    public NbFarmMarket selectById(Integer id) {
        return marketMapper.selectById(id);
    }
    
    @Override
    public int insert(NbFarmMarket market) {
        return marketMapper.insert(market);
    }
    
    @Override
    public int update(NbFarmMarket market) {
        return marketMapper.update(market);
    }
    
    @Override
    public int deleteById(Integer id) {
        return marketMapper.deleteById(id);
    }
}

