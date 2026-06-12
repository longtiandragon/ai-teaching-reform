package org.nong.service.impl;

import org.nong.common.Result;
import org.nong.entity.NbExpert;
import org.nong.mapper.NbExpertMapper;
import org.nong.service.INbExpertService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class NbExpertServiceImpl implements INbExpertService {
    
    @Autowired
    private NbExpertMapper expertMapper;
    
    @Override
    @SuppressWarnings("unchecked")
    public Result<NbExpert> selectList(Map<String, Object> params) {
        List<NbExpert> list = expertMapper.selectList(params);
        Long total = expertMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);
        result.setTotal(total);
        result.buildPageData();
        return result;
    }
    
    @Override
    public NbExpert selectById(String id) {
        return expertMapper.selectById(id);
    }
    
    @Override
    public int insert(NbExpert expert) {
        if (expert.getId() == null || expert.getId().isEmpty()) {
            expert.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return expertMapper.insert(expert);
    }
    
    @Override
    public int update(NbExpert expert) {
        return expertMapper.update(expert);
    }
    
    @Override
    public int deleteById(String id) {
        return expertMapper.deleteById(id);
    }
    
    @Override
    public int deleteBatch(String[] ids) {
        return expertMapper.deleteBatch(ids);
    }
}

