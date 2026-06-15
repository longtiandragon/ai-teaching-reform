package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.NbCreditLoan;
import com.movie.nbspringproduct.mapper.NbCreditLoanMapper;
import com.movie.nbspringproduct.service.INbCreditLoanService;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.Date;
import java.util.List;

/**
 * 信贷信息Service实现类
 */
@Service
public class NbCreditLoanServiceImpl extends ServiceImpl<NbCreditLoanMapper, NbCreditLoan> 
        implements INbCreditLoanService {
    
    @Override
    public List<NbCreditLoan> selectCreditLoanList(NbCreditLoan loan) {
        LambdaQueryWrapper<NbCreditLoan> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.isNotBlank(loan.getTitle()), NbCreditLoan::getTitle, loan.getTitle());
        wrapper.eq(StringUtils.isNotBlank(loan.getAuthor()), NbCreditLoan::getAuthor, loan.getAuthor());
        wrapper.eq(loan.getPublishStatus() != null, NbCreditLoan::getPublishStatus, loan.getPublishStatus());
        wrapper.eq(loan.getRecommend() != null, NbCreditLoan::getRecommend, loan.getRecommend());
        wrapper.orderByDesc(NbCreditLoan::getCreateTime);
        return this.list(wrapper);
    }
    
    @Override
    public NbCreditLoan selectCreditLoanById(String id) {
        return this.getById(id);
    }
    
    @Override
    public int insertCreditLoan(NbCreditLoan loan) {
        if (loan.getBrowseNum() == null) {
            loan.setBrowseNum(0);
        }
        if (loan.getPublishStatus() == null) {
            loan.setPublishStatus(0);
        }
        if (loan.getRecommend() == null) {
            loan.setRecommend(0);
        }
        return this.save(loan) ? 1 : 0;
    }
    
    @Override
    public int updateCreditLoan(NbCreditLoan loan) {
        return this.updateById(loan) ? 1 : 0;
    }
    
    @Override
    public int deleteCreditLoanByIds(String[] ids) {
        return this.removeByIds(Arrays.asList(ids)) ? 1 : 0;
    }
    
    @Override
    public int recommandCreditLoan(String[] ids) {
        List<NbCreditLoan> list = this.listByIds(Arrays.asList(ids));
        for (NbCreditLoan loan : list) {
            loan.setRecommend(1);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int unRecommandCreditLoan(String[] ids) {
        List<NbCreditLoan> list = this.listByIds(Arrays.asList(ids));
        for (NbCreditLoan loan : list) {
            loan.setRecommend(0);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int publishCreditLoan(String[] ids) {
        List<NbCreditLoan> list = this.listByIds(Arrays.asList(ids));
        for (NbCreditLoan loan : list) {
            loan.setPublishStatus(1);
            loan.setPublishTime(new Date());
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int unPublishCreditLoan(String[] ids) {
        List<NbCreditLoan> list = this.listByIds(Arrays.asList(ids));
        for (NbCreditLoan loan : list) {
            loan.setPublishStatus(0);
            loan.setPublishTime(null);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
}

