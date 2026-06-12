package org.nong.service;

import org.nong.common.Result;
import org.nong.entity.SysUser;

import java.util.Map;

/**
 * 系统用户Service接口
 */
public interface ISysUserService {
    
    /**
     * 查询用户列表
     */
    Result<SysUser> selectList(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    SysUser selectById(String id);
    
    /**
     * 根据用户名查询
     */
    SysUser selectByUsername(String username);
    
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
    int deleteById(String id);
    
    /**
     * 重置密码
     */
    int resetPassword(String id, String password);
}

