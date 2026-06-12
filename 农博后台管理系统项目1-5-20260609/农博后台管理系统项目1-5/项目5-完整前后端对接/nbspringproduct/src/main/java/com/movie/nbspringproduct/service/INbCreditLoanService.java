package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.NbCreditLoan;

import java.util.List;

/**
 * 信贷信息Service接口
 */
public interface INbCreditLoanService extends IService<NbCreditLoan> {
    
    /**
     * 查询信贷信息列表
     */
    List<NbCreditLoan> selectCreditLoanList(NbCreditLoan loan);
    
    /**
     * 查询信贷信息详细
     */
    NbCreditLoan selectCreditLoanById(String id);
    
    /**
     * 新增信贷信息
     */
    int insertCreditLoan(NbCreditLoan loan);
    
    /**
     * 修改信贷信息
     */
    int updateCreditLoan(NbCreditLoan loan);
    
    /**
     * 批量删除信贷信息
     */
    int deleteCreditLoanByIds(String[] ids);
    
    /**
     * 推荐信贷信息
     */
    int recommandCreditLoan(String[] ids);
    
    /**
     * 取消推荐信贷信息
     */
    int unRecommandCreditLoan(String[] ids);
    
    /**
     * 发布信贷信息
     */
    int publishCreditLoan(String[] ids);
    
    /**
     * 取消发布信贷信息
     */
    int unPublishCreditLoan(String[] ids);
}

