package com.itheima.dao.impl;

import cn.hutool.core.io.IoUtil;
import com.itheima.dao.UserDao;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

/**
 * 数据访问 - 数据的增删改查
 */
public class UserDaoImpl implements UserDao {
    @Override
    public List<String> list() {
        //1. 读取user.txt中的数据
        InputStream in = this.getClass().getClassLoader().getResourceAsStream("user.txt");
        ArrayList<String> lines = IoUtil.readUtf8Lines(in, new ArrayList<>());
        return lines;
    }
}
