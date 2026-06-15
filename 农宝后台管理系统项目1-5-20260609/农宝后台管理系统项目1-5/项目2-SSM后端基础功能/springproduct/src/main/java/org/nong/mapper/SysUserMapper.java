package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.SysUser;

import java.util.List;
import java.util.Map;

/**
 * 系统用户Mapper接口
 */
public interface SysUserMapper {
    
    /**
     * 查询用户列表
     */
    List<SysUser> selectList(Map<String, Object> params);
    
    /**
     * 查询总数
     */
    Long selectCount(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    SysUser selectById(@Param("id") String id);
    
    /**
     * 根据用户名查询
     */
    SysUser selectByUsername(@Param("username") String username);
    
    /**
     * 新增
     */
    int insert(SysUser user);
    
    /**
     * 修改
     */
    int update(SysUser user);
    
    /**
     * 删除
     */
    int deleteById(@Param("id") String id);
    
    /**
     * 重置密码
     */
    int resetPassword(@Param("id") String id, @Param("password") String password);
}

