package com.itheima.service.impl;

import com.itheima.dao.UserDao;
import com.itheima.dao.impl.UserDaoImpl;
import com.itheima.pojo.User;
import com.itheima.service.UserService;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

public class UserServiceImpl implements UserService {
    
    private UserDao userDao = new UserDaoImpl();
    @Override
    public List<User> list() {
        //1. 调用dao层, 获取数据
        List<String> lines = userDao.list();

        //2. 业务逻辑处理: 解析数据, 封装User对象 --> List<User>
        List<User> userList = lines.stream().map(line -> {
            String[] split = line.split(",");
            return new User(
                    Integer.parseInt(split[0]),
                    split[1],
                    split[2],
                    split[3],
                    Integer.parseInt(split[4]),
                    LocalDateTime.parse(split[5], DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        }).toList();
        return userList;
    }
}
