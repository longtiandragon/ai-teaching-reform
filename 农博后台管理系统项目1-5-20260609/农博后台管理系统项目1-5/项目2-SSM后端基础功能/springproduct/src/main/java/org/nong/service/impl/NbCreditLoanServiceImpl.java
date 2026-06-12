package org.nong.service.impl;

import org.nong.common.Result;
import org.nong.entity.NbCreditLoan;
import org.nong.mapper.NbCreditLoanMapper;
import org.nong.service.INbCreditLoanService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class NbCreditLoanServiceImpl implements INbCreditLoanService {
    
    @Autowired
    private NbCreditLoanMapper loanMapper;
    
    @Override
    @SuppressWarnings("unchecked")
    public Result<NbCreditLoan> selectList(Map<String, Object> params) {
        List<NbCreditLoan> list = loanMapper.selectList(params);
        Long total = loanMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);
        result.setTotal(total);
        result.buildPageData();
        return result;
    }
    
    @Override
    public NbCreditLoan selectById(String id) {
        return loanMapper.selectById(id);
    }
    
    @Override
    public int insert(NbCreditLoan loan) {
        if (loan.getId() == null || loan.getId().isEmpty()) {
            loan.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return loanMapper.insert(loan);
    }
    
    @Override
    public int update(NbCreditLoan loan) {
        return loanMapper.update(loan);
    }
    
    @Override
    public int deleteById(String id) {
        return loanMapper.deleteById(id);
    }
    
    @Override
    public int deleteBatch(String[] ids) {
        return loanMapper.deleteBatch(ids);
    }
}

