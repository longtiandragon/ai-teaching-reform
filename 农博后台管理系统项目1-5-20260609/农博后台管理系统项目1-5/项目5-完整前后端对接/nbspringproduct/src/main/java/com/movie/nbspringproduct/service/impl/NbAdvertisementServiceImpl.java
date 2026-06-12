package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.NbAdvertisement;
import com.movie.nbspringproduct.mapper.NbAdvertisementMapper;
import com.movie.nbspringproduct.service.INbAdvertisementService;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;

/**
 * 广告Service实现类
 */
@Service
public class NbAdvertisementServiceImpl extends ServiceImpl<NbAdvertisementMapper, NbAdvertisement> 
        implements INbAdvertisementService {
    
    @Override
    public List<NbAdvertisement> selectAdvertisementList(NbAdvertisement advertisement) {
        LambdaQueryWrapper<NbAdvertisement> wrapper = new LambdaQueryWrapper<>();
        
        // 条件查询
        wrapper.like(StringUtils.isNotBlank(advertisement.getTitle()), 
                NbAdvertisement::getTitle, advertisement.getTitle());
        wrapper.eq(StringUtils.isNotBlank(advertisement.getPosition()), 
                NbAdvertisement::getPosition, advertisement.getPosition());
        wrapper.eq(advertisement.getStatus() != null, 
                NbAdvertisement::getStatus, advertisement.getStatus());
        
        // 排序：优先按排序号，然后按创建时间降序
        wrapper.orderByAsc(NbAdvertisement::getSort)
               .orderByDesc(NbAdvertisement::getCreateTime);
        
        return this.list(wrapper);
    }
    
    @Override
    public NbAdvertisement selectAdvertisementById(String id) {
        return this.getById(id);
    }
    
    @Override
    public int insertAdvertisement(NbAdvertisement advertisement) {
        if (advertisement.getClickCount() == null) {
            advertisement.setClickCount(0);
        }
        if (advertisement.getStatus() == null) {
            advertisement.setStatus(0);
        }
        if (advertisement.getSort() == null) {
            advertisement.setSort(0);
        }
        return this.save(advertisement) ? 1 : 0;
    }
    
    @Override
    public int updateAdvertisement(NbAdvertisement advertisement) {
        return this.updateById(advertisement) ? 1 : 0;
    }
    
    @Override
    public int deleteAdvertisementByIds(String[] ids) {
        return this.removeByIds(Arrays.asList(ids)) ? 1 : 0;
    }
    
    @Override
    public int publishAdvertisement(String[] ids) {
        List<NbAdvertisement> list = this.listByIds(Arrays.asList(ids));
        for (NbAdvertisement advertisement : list) {
            advertisement.setStatus(1);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int unpublishAdvertisement(String[] ids) {
        List<NbAdvertisement> list = this.listByIds(Arrays.asList(ids));
        for (NbAdvertisement advertisement : list) {
            advertisement.setStatus(0);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
}

