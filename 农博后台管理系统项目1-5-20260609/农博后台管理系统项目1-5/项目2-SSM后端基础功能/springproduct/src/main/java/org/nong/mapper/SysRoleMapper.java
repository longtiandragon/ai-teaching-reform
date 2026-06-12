package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.SysRole;

import java.util.List;
import java.util.Map;

/**
 * 角色Mapper接口
 */
public interface SysRoleMapper {
    
    /**
     * 查询角色列表
     */
    List<SysRole> selectList(Map<String, Object> params);
    
    /**
     * 查询总数
     */
    Long selectCount(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    SysRole selectById(@Param("id") String id);
    
    /**
     * 新增
     */
    int insert(SysRole role);
    
    /**
     * 修改
     */
    int update(SysRole role);
    
    /**
     * 删除
     */
    int deleteById(@Param("id") String id);
}

