package com.movie.nbspringproduct.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.movie.nbspringproduct.entity.TestUser;
import org.apache.ibatis.annotations.Mapper;

/**
 * 测试用户Mapper接口
 */
@Mapper
public interface TestUserMapper extends BaseMapper<TestUser> {
}

