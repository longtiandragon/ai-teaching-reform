package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.NbCreditLoan;

import java.util.List;
import java.util.Map;

/**
 * 信贷信息Mapper接口
 */
public interface NbCreditLoanMapper {
    
    /**
     * 查询信贷信息列表
     */
    List<NbCreditLoan> selectList(Map<String, Object> params);
    
    /**
     * 查询总数
     */
    Long selectCount(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    NbCreditLoan selectById(@Param("id") String id);
    
    /**
     * 新增
     */
    int insert(NbCreditLoan loan);
    
    /**
     * 修改
     */
    int update(NbCreditLoan loan);
    
    /**
     * 删除
     */
    int deleteById(@Param("id") String id);
    
    /**
     * 批量删除
     */
    int deleteBatch(@Param("ids") String[] ids);
}

