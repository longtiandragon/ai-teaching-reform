package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.SysUser;

/**
 * 系统用户Service接口
 */
public interface ISysUserService extends IService<SysUser> {
    
    /**
     * 重置用户密码
     * @param userId 用户ID
     * @return 新密码
     */
    String resetPassword(String userId);
}

