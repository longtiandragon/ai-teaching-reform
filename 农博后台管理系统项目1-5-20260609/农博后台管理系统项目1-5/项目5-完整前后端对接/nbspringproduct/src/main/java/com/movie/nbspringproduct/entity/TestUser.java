package com.movie.nbspringproduct.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.io.Serializable;

/**
 * 测试用户实体类
 */
@Data
@TableName("test_user")
public class TestUser implements Serializable {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 用户ID
     */
    @TableId(type = IdType.AUTO)
    private Integer userId;
    
    /**
     * 用户名称
     */
    private String username;
    
    /**
     * 用户手机
     */
    private String mobile;
    
    /**
     * 用户密码
     */
    private String password;
}

