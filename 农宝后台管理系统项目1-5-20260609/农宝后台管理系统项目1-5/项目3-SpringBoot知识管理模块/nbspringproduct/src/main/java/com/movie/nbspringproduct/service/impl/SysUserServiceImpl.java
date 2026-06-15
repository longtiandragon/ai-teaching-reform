package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.SysUser;
import com.movie.nbspringproduct.mapper.SysUserMapper;
import com.movie.nbspringproduct.service.ISysUserService;
import org.springframework.stereotype.Service;

/**
 * 系统用户Service实现类
 */
@Service
public class SysUserServiceImpl extends ServiceImpl<SysUserMapper, SysUser> implements ISysUserService {
    
    @Override
    public String resetPassword(String userId) {
        // 默认密码
        String defaultPassword = "123456";
        
        SysUser user = getById(userId);
        if (user != null) {
            // 实际项目中应该加密密码，这里为了简单直接存储
            user.setPassword(defaultPassword);
            updateById(user);
        }
        
        return defaultPassword;
    }
}

