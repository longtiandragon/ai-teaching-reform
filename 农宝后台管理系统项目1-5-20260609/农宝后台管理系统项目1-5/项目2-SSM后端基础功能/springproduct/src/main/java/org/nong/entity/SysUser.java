package org.nong.entity;

import lombok.Data;

import java.io.Serializable;

/**
 * 系统用户实体类
 */
@Data
public class SysUser implements Serializable {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 用户ID
     */
    private String id;
    
    /**
     * 用户名
     */
    private String username;
    
    /**
     * 昵称
     */
    private String nickname;
    
    /**
     * 密码
     */
    private String password;
    
    /**
     * 邮箱
     */
    private String email;
    
    /**
     * 手机号码
     */
    private String phonenumber;
    
    /**
     * 用户性别（0男 1女 2未知）
     */
    private Integer sex;
    
    /**
     * 头像地址
     */
    private String avatar;
    
    /**
     * 状态（0正常 1停用）
     */
    private Integer status;
    
    /**
     * 删除标志（0代表存在 1代表删除）
     */
    private Integer delFlag;
    
    /**
     * 最后登录IP
     */
    private String loginIp;
    
    /**
     * 最后登录时间
     */
    private String loginDate;
    
    /**
     * 备注
     */
    private String remark;
    
    /**
     * 创建时间
     */
    private String createTime;
    
    /**
     * 更新时间
     */
    private String updateTime;
}

