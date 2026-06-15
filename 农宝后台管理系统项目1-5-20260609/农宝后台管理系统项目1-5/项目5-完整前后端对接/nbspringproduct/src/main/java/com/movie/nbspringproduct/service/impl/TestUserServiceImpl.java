package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.TestUser;
import com.movie.nbspringproduct.mapper.TestUserMapper;
import com.movie.nbspringproduct.service.ITestUserService;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 测试用户Service实现类
 */
@Service
public class TestUserServiceImpl extends ServiceImpl<TestUserMapper, TestUser> 
        implements ITestUserService {
    
    @Override
    public List<TestUser> selectUserList() {
        return this.list();
    }
    
    @Override
    public TestUser selectUserById(Integer userId) {
        return this.getById(userId);
    }
    
    @Override
    public int insertUser(TestUser user) {
        return this.save(user) ? 1 : 0;
    }
    
    @Override
    public int updateUser(TestUser user) {
        return this.updateById(user) ? 1 : 0;
    }
    
    @Override
    public int deleteUserById(Integer userId) {
        return this.removeById(userId) ? 1 : 0;
    }
}

