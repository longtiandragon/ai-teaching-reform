package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.TestUser;

import java.util.List;

/**
 * 测试用户Service接口
 */
public interface ITestUserService extends IService<TestUser> {
    
    /**
     * 查询用户列表
     */
    List<TestUser> selectUserList();
    
    /**
     * 查询用户详细
     */
    TestUser selectUserById(Integer userId);
    
    /**
     * 新增用户
     */
    int insertUser(TestUser user);
    
    /**
     * 修改用户
     */
    int updateUser(TestUser user);
    
    /**
     * 删除用户
     */
    int deleteUserById(Integer userId);
}

