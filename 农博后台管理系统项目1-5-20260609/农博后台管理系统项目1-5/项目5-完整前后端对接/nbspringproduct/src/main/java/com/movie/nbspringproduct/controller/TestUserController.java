package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.TestUser;
import com.movie.nbspringproduct.service.ITestUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 测试用户Controller
 */
@RestController
@RequestMapping("/dev-api/test/user")
public class TestUserController {
    
    @Autowired
    private ITestUserService testUserService;
    
    /**
     * 获取用户列表
     */
    @GetMapping("/list")
    public Result<List<TestUser>> list() {
        List<TestUser> list = testUserService.selectUserList();
        return Result.success(list);
    }
    
    /**
     * 获取用户详细
     */
    @GetMapping("/{userId}")
    public Result<TestUser> getInfo(@PathVariable("userId") Integer userId) {
        return Result.success(testUserService.selectUserById(userId));
    }
    
    /**
     * 新增用户
     */
    @PostMapping("/save")
    public Result<String> save(TestUser user) {
        return testUserService.insertUser(user) > 0 ? 
                Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 更新用户
     */
    @PutMapping("/update")
    public Result<TestUser> update(@RequestBody TestUser user) {
        return testUserService.updateUser(user) > 0 ? 
                Result.success("更新成功", user) : Result.error("更新失败");
    }
    
    /**
     * 删除用户信息
     */
    @DeleteMapping("/{userId}")
    public Result<String> remove(@PathVariable("userId") Integer userId) {
        return testUserService.deleteUserById(userId) > 0 ? 
                Result.success("删除成功") : Result.error("删除失败");
    }
}

