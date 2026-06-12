package org.nong.service.impl;

import org.nong.common.Result;
import org.nong.entity.NbFarmProduce;
import org.nong.mapper.NbFarmProduceMapper;
import org.nong.service.INbFarmProduceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 农产品Service实现类
 */
@Service
public class NbFarmProduceServiceImpl implements INbFarmProduceService {
    
    @Autowired
    private NbFarmProduceMapper produceMapper;
    
    @Override
    @SuppressWarnings("unchecked")
    public Result<NbFarmProduce> selectList(Map<String, Object> params) {
        List<NbFarmProduce> list = produceMapper.selectList(params);
        Long total = produceMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);
        result.setTotal(total);
        result.buildPageData();
        return result;
    }
    
    @Override
    public NbFarmProduce selectById(String id) {
        return produceMapper.selectById(id);
    }
    
    @Override
    public int insert(NbFarmProduce produce) {
        if (produce.getId() == null || produce.getId().isEmpty()) {
            produce.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return produceMapper.insert(produce);
    }
    
    @Override
    public int update(NbFarmProduce produce) {
        return produceMapper.update(produce);
    }
    
    @Override
    public int deleteById(String id) {
        return produceMapper.deleteById(id);
    }
    
    @Override
    public int deleteBatch(String[] ids) {
        return produceMapper.deleteBatch(ids);
    }
}

