package com.itheima.service.impl;

import com.itheima.mapper.EmpMapper;
import com.itheima.pojo.Emp;
import com.itheima.pojo.PageResult;
import com.itheima.service.EmpService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class EmpServiceImpl implements EmpService {

    @Autowired
    private EmpMapper empMapper;

    @Override
    public PageResult<Emp> page(Integer page, Integer pageSize) {
        //1. 获取总记录数 total
        Long total = empMapper.count();

        //2. 获取分页查询结果列表 rows
        //2.1 计算起始索引
        Integer start = (page - 1) * pageSize;
        //2.2 执行查询
        List<Emp> empList = empMapper.list(start, pageSize);

        //3. 封装分页结果
        return new PageResult<>(total, empList);
    }

}
