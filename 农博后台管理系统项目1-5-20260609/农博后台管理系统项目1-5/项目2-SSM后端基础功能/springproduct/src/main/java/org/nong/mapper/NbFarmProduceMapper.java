package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.NbFarmProduce;

import java.util.List;
import java.util.Map;

/**
 * 农产品Mapper接口
 */
public interface NbFarmProduceMapper {
    
    /**
     * 查询农产品列表
     */
    List<NbFarmProduce> selectList(Map<String, Object> params);
    
    /**
     * 查询总数
     */
    Long selectCount(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    NbFarmProduce selectById(@Param("id") String id);
    
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
    int deleteById(@Param("id") String id);
    
    /**
     * 批量删除
     */
    int deleteBatch(@Param("ids") String[] ids);
}

