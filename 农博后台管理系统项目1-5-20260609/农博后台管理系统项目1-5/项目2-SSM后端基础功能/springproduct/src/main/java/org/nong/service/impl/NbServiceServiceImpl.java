package org.nong.service.impl;

import org.nong.common.Result;
import org.nong.entity.NbService;
import org.nong.mapper.NbServiceMapper;
import org.nong.service.INbServiceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class NbServiceServiceImpl implements INbServiceService {
    
    @Autowired
    private NbServiceMapper serviceMapper;
    
    @Override
    @SuppressWarnings("unchecked")
    public Result<NbService> selectList(Map<String, Object> params) {
        List<NbService> list = serviceMapper.selectList(params);
        Long total = serviceMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);
        result.setTotal(total);
        result.buildPageData();
        return result;
    }
    
    @Override
    public NbService selectById(String id) {
        return serviceMapper.selectById(id);
    }
    
    @Override
    public int insert(NbService service) {
        if (service.getId() == null || service.getId().isEmpty()) {
            service.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return serviceMapper.insert(service);
    }
    
    @Override
    public int update(NbService service) {
        return serviceMapper.update(service);
    }
    
    @Override
    public int deleteById(String id) {
        return serviceMapper.deleteById(id);
    }
    
    @Override
    public int deleteBatch(String[] ids) {
        return serviceMapper.deleteBatch(ids);
    }
}

