package org.nong.service.impl;

import org.nong.common.Result;
import org.nong.entity.SysUser;
import org.nong.mapper.SysUserMapper;
import org.nong.service.ISysUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 系统用户Service实现类
 */
@Service
public class SysUserServiceImpl implements ISysUserService {
    
    @Autowired
    private SysUserMapper userMapper;
    
    @Override
    @SuppressWarnings("unchecked")
    public Result<SysUser> selectList(Map<String, Object> params) {
        List<SysUser> list = userMapper.selectList(params);
        Long total = userMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);
        result.setTotal(total);
        result.buildPageData();
        return result;
    }
    
    @Override
    public SysUser selectById(String id) {
        return userMapper.selectById(id);
    }
    
    @Override
    public SysUser selectByUsername(String username) {
        return userMapper.selectByUsername(username);
    }
    
    @Override
    public int insert(SysUser user) {
        if (user.getId() == null || user.getId().isEmpty()) {
            user.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return userMapper.insert(user);
    }
    
    @Override
    public int update(SysUser user) {
        return userMapper.update(user);
    }
    
    @Override
    public int deleteById(String id) {
        return userMapper.deleteById(id);
    }
    
    @Override
    public int resetPassword(String id, String password) {
        return userMapper.resetPassword(id, password);
    }
}

