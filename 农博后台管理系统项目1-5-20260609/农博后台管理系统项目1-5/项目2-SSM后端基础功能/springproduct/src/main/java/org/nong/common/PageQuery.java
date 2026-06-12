package org.nong.common;

import lombok.Data;

/**
 * 分页查询参数
 */
@Data
public class PageQuery {
    
    /**
     * 当前页码
     */
    private Integer pageNum = 1;
    
    /**
     * 每页记录数
     */
    private Integer pageSize = 10;
    
    /**
     * 排序字段
     */
    private String orderByColumn;
    
    /**
     * 排序方式（asc/desc）
     */
    private String isAsc = "asc";
    
    /**
     * 计算起始行号
     */
    public Integer getOffset() {
        return (pageNum - 1) * pageSize;
    }
}

