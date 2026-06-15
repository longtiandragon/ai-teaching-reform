package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.NbFarmMarket;
import com.movie.nbspringproduct.mapper.NbFarmMarketMapper;
import com.movie.nbspringproduct.service.INbFarmMarketService;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;

/**
 * 农贸市场Service实现类
 */
@Service
public class NbFarmMarketServiceImpl extends ServiceImpl<NbFarmMarketMapper, NbFarmMarket> 
        implements INbFarmMarketService {
    
    @Override
    public List<NbFarmMarket> selectFarmMarketList(NbFarmMarket market) {
        LambdaQueryWrapper<NbFarmMarket> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.isNotBlank(market.getName()), NbFarmMarket::getName, market.getName());
        wrapper.eq(StringUtils.isNotBlank(market.getRegionId()), NbFarmMarket::getRegionId, market.getRegionId());
        wrapper.orderByDesc(NbFarmMarket::getCreateTime);
        return this.list(wrapper);
    }
    
    @Override
    public NbFarmMarket selectFarmMarketById(Integer id) {
        return this.getById(id);
    }
    
    @Override
    public int insertFarmMarket(NbFarmMarket market) {
        return this.save(market) ? 1 : 0;
    }
    
    @Override
    public int updateFarmMarket(NbFarmMarket market) {
        return this.updateById(market) ? 1 : 0;
    }
    
    @Override
    public int deleteFarmMarketByIds(Integer[] ids) {
        return this.removeByIds(Arrays.asList(ids)) ? 1 : 0;
    }
}

