package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.NbFarmProduce;

import java.util.List;

/**
 * 农产品Service接口
 */
public interface INbFarmProduceService extends IService<NbFarmProduce> {
    
    /**
     * 查询农产品列表
     */
    List<NbFarmProduce> selectFarmProduceList(NbFarmProduce produce);
    
    /**
     * 查询农产品详细
     */
    NbFarmProduce selectFarmProduceById(String id);
    
    /**
     * 新增农产品
     */
    int insertFarmProduce(NbFarmProduce produce);
    
    /**
     * 修改农产品
     */
    int updateFarmProduce(NbFarmProduce produce);
    
    /**
     * 批量删除农产品
     */
    int deleteFarmProduceByIds(String[] ids);
    
    /**
     * 推荐农产品
     */
    int recommendFarmProduce(String[] ids);
    
    /**
     * 取消推荐农产品
     */
    int unrecommendFarmProduce(String[] ids);
    
    /**
     * 发布农产品
     */
    int pushFarmProduce(String[] ids);
    
    /**
     * 取消发布农产品
     */
    int unpushFarmProduce(String[] ids);
}

