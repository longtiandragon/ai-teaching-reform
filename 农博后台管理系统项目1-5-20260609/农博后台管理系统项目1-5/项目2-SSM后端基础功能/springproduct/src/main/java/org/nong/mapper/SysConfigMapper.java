package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.SysConfig;

import java.util.List;

/**
 * 系统配置Mapper接口
 */
public interface SysConfigMapper {
    
    /**
     * 查询所有配置
     */
    List<SysConfig> selectAll();
    
    /**
     * 根据ID查询
     */
    SysConfig selectById(@Param("id") String id);
    
    /**
     * 根据配置键查询
     */
    SysConfig selectByKey(@Param("configKey") String configKey);
    
    /**
     * 新增
     */
    int insert(SysConfig config);
    
    /**
     * 修改
     */
    int update(SysConfig config);
    
    /**
     * 根据配置键更新
     */
    int updateByKey(SysConfig config);
}

