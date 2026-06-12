package com.itheima.controller;

import com.itheima.pojo.User;
import com.itheima.service.UserService;
import jakarta.annotation.Resource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

/**
 * 用户信息Controller
 */
@RestController // @ResponseBody -> 作用: 将controller返回值直接作为响应体的数据直接响应; 返回值是对象/集合->json->响应
public class UserController {

    //方式一: 属性注入
    //@Autowired
    //private UserService userService;

    //方式二: 构造器注入
    //private final UserService userService;
    ////@Autowired ---> 如果当前类中只存在一个构造函数, @Autowired可以省略
    //public UserController(UserService userService) {
    //    this.userService = userService;
    //}

    //方式三: setter注入
    //private UserService userService;
    //@Autowired
    //public void setUserService(UserService userService) {
    //    this.userService = userService;
    //}

    //@Qualifier("userServiceImpl")
    //@Autowired
    //private UserService userService;

    @Resource(name = "userServiceImpl2")
    private UserService userService;

    @RequestMapping("/list")
    public List<User> list() throws Exception {
        //1. 调用service, 获取数据
        List<User> userList = userService.findAll();

        //2. 返回数据(json)
        return userList;
    }

}
