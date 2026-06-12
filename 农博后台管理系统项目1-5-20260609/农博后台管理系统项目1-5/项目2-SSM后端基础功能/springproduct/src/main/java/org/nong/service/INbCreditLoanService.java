package org.nong.service;

import org.nong.common.Result;
import org.nong.entity.NbCreditLoan;
import java.util.Map;

public interface INbCreditLoanService {
    Result<NbCreditLoan> selectList(Map<String, Object> params);
    NbCreditLoan selectById(String id);
    int insert(NbCreditLoan loan);
    int update(NbCreditLoan loan);
    int deleteById(String id);
    int deleteBatch(String[] ids);
}

