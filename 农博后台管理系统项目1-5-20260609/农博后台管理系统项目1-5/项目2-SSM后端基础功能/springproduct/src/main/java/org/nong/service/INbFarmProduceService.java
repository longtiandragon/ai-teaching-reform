package org.nong.service;

import org.nong.common.Result;
import org.nong.entity.NbFarmProduce;

import java.util.Map;

/**
 * 农产品Service接口
 */
public interface INbFarmProduceService {
    
    /**
     * 查询农产品列表
     */
    Result<NbFarmProduce> selectList(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    NbFarmProduce selectById(String id);
    
    /**
     * 新增
     */
    int insert(NbFarmProduce produce);
    
    /**
     * 修改
     */
    int update(NbFarmProduce produce);
    
    /**
     * 删除
     */
    int deleteById(String id);
    
    /**
     * 批量删除
     */
    int deleteBatch(String[] ids);
}

