package org.nong.common;

import lombok.Data;

import java.io.Serializable;

/**
 * 通用响应结果类
 */
@Data
public class Result<T> implements Serializable {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 状态码
     */
    private Integer code;
    
    /**
     * 返回消息
     */
    private String msg;
    
    /**
     * 返回数据
     */
    private T data;
    
    /**
     * 总记录数
     */
    private Long total;
    
    /**
     * 列表数据
     */
    private T rows;
    
    public Result() {
    }
    
    public Result(Integer code, String msg) {
        this.code = code;
        this.msg = msg;
    }
    
    public Result(Integer code, String msg, T data) {
        this.code = code;
        this.msg = msg;
        this.data = data;
    }
    
    /**
     * 成功响应
     */
    public static <T> Result<T> success() {
        return new Result<>(200, "操作成功");
    }
    
    /**
     * 成功响应带消息
     */
    public static <T> Result<T> success(String msg) {
        return new Result<>(200, msg);
    }
    
    /**
     * 成功响应带数据
     */
    public static <T> Result<T> success(T data) {
        Result<T> result = new Result<>(200, "操作成功");
        result.setData(data);
        return result;
    }
    
    /**
     * 成功响应带消息和数据
     */
    public static <T> Result<T> success(String msg, T data) {
        Result<T> result = new Result<>(200, msg);
        result.setData(data);
        return result;
    }
    
    /**
     * 分页成功响应
     */
    public static <T> Result<T> success(T rows, Long total) {
        Result<T> result = new Result<>(200, "查询成功");
        result.setRows(rows);
        result.setTotal(total);
        return result;
    }
    
    /**
     * 构建分页数据（兼容MyBatis-Plus格式）
     */
    public void buildPageData() {
        if (this.rows != null) {
            PageData<T> pageData = new PageData<>();
            pageData.setRecords(this.rows);
            pageData.setTotal(this.total);
            this.data = (T) pageData;
        }
    }
    
    /**
     * 分页数据内部类
     */
    @Data
    public static class PageData<T> {
        private T records;
        private Long total;
    }
    
    /**
     * 失败响应
     */
    public static <T> Result<T> error() {
        return new Result<>(500, "操作失败");
    }
    
    /**
     * 失败响应带消息
     */
    public static <T> Result<T> error(String msg) {
        return new Result<>(500, msg);
    }
    
    /**
     * 失败响应带状态码和消息
     */
    public static <T> Result<T> error(Integer code, String msg) {
        return new Result<>(code, msg);
    }
}

