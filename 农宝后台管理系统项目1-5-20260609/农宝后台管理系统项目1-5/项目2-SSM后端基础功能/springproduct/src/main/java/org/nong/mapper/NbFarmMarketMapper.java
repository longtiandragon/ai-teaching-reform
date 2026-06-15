package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.NbFarmMarket;

import java.util.List;
import java.util.Map;

/**
 * 农贸市场Mapper接口
 */
public interface NbFarmMarketMapper {
    
    /**
     * 查询农贸市场列表
     */
    List<NbFarmMarket> selectList(Map<String, Object> params);
    
    /**
     * 查询总数
     */
    Long selectCount(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    NbFarmMarket selectById(@Param("id") Integer id);
    
    /**
     * 新增
     */
    int insert(NbFarmMarket market);
    
    /**
     * 修改
     */
    int update(NbFarmMarket market);
    
    /**
     * 删除
     */
    int deleteById(@Param("id") Integer id);
}

