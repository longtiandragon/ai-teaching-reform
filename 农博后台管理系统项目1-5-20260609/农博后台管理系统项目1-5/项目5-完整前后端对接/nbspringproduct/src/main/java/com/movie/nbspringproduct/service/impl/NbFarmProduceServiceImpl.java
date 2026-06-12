package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.NbFarmProduce;
import com.movie.nbspringproduct.mapper.NbFarmProduceMapper;
import com.movie.nbspringproduct.service.INbFarmProduceService;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.Date;
import java.util.List;

/**
 * 农产品Service实现类
 */
@Service
public class NbFarmProduceServiceImpl extends ServiceImpl<NbFarmProduceMapper, NbFarmProduce> 
        implements INbFarmProduceService {
    
    @Override
    public List<NbFarmProduce> selectFarmProduceList(NbFarmProduce produce) {
        LambdaQueryWrapper<NbFarmProduce> wrapper = new LambdaQueryWrapper<>();
        
        // 条件查询
        wrapper.like(StringUtils.isNotBlank(produce.getTitle()), NbFarmProduce::getTitle, produce.getTitle());
        wrapper.eq(StringUtils.isNotBlank(produce.getCatgory()), NbFarmProduce::getCatgory, produce.getCatgory());
        wrapper.eq(StringUtils.isNotBlank(produce.getProduceType()), NbFarmProduce::getProduceType, produce.getProduceType());
        wrapper.eq(produce.getPushStatus() != null, NbFarmProduce::getPushStatus, produce.getPushStatus());
        wrapper.eq(produce.getRecommend() != null, NbFarmProduce::getRecommend, produce.getRecommend());
        wrapper.eq(StringUtils.isNotBlank(produce.getProviderName()), NbFarmProduce::getProviderName, produce.getProviderName());
        
        // 排序：优先按创建时间降序
        wrapper.orderByDesc(NbFarmProduce::getCreateTime);
        
        // 注意：这里返回所有数据，BLOB字段可能导致性能问题
        // 建议：如果只需要列表展示，可以考虑不查询 description 等大字段
        return this.list(wrapper);
    }
    
    @Override
    public NbFarmProduce selectFarmProduceById(String id) {
        return this.getById(id);
    }
    
    @Override
    public int insertFarmProduce(NbFarmProduce produce) {
        if (produce.getBrowseNum() == null) {
            produce.setBrowseNum(0);
        }
        if (produce.getPushStatus() == null) {
            produce.setPushStatus(0);
        }
        if (produce.getRecommend() == null) {
            produce.setRecommend(0);
        }
        return this.save(produce) ? 1 : 0;
    }
    
    @Override
    public int updateFarmProduce(NbFarmProduce produce) {
        return this.updateById(produce) ? 1 : 0;
    }
    
    @Override
    public int deleteFarmProduceByIds(String[] ids) {
        return this.removeByIds(Arrays.asList(ids)) ? 1 : 0;
    }
    
    @Override
    public int recommendFarmProduce(String[] ids) {
        List<NbFarmProduce> list = this.listByIds(Arrays.asList(ids));
        for (NbFarmProduce produce : list) {
            produce.setRecommend(1);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int unrecommendFarmProduce(String[] ids) {
        List<NbFarmProduce> list = this.listByIds(Arrays.asList(ids));
        for (NbFarmProduce produce : list) {
            produce.setRecommend(0);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int pushFarmProduce(String[] ids) {
        List<NbFarmProduce> list = this.listByIds(Arrays.asList(ids));
        for (NbFarmProduce produce : list) {
            produce.setPushStatus(1);
            produce.setPushTime(new Date());
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int unpushFarmProduce(String[] ids) {
        List<NbFarmProduce> list = this.listByIds(Arrays.asList(ids));
        for (NbFarmProduce produce : list) {
            produce.setPushStatus(0);
            produce.setPushTime(null);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
}

