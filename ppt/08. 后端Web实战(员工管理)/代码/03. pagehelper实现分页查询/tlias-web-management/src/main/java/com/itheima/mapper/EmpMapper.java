package com.itheima.mapper;

import com.itheima.pojo.Emp;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import java.util.List;

/**
 * 操作员工信息的Mapper
 */
@Mapper
public interface EmpMapper {

    /**
     * 查询员工信息
     */
    //@Select("select emp.*, dept.name as dept_name from emp left join dept on emp.dept_id = dept.id limit #{start},#{pageSize}")
    //public List<Emp> list(Integer start, Integer pageSize);

    /**
     * 获取符合条件的总记录数
     */
    //@Select("select count(*) from emp left join dept on emp.dept_id = dept.id")
    //Long count();

    /**
     * 查询员工信息
     */
    @Select("select emp.*, dept.name as dept_name from emp left join dept on emp.dept_id = dept.id")
    public List<Emp> list();
}
