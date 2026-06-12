package com.itheima;

import com.itheima.mapper.EmpMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class TliasWebManagementApplicationTests {

    @Autowired
    private EmpMapper empMapper;

    /**
     * 测试查询员工信息方法
     */
    @Test
    public void testList() {
        //empMapper.list().forEach(System.out::println);
    }
}
