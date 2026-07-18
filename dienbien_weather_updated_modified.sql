
IF DB_ID('dienbien_weather') IS NULL
    CREATE DATABASE dienbien_weather;
GO

USE dienbien_weather;
GO
USE dienbien_weather;

IF OBJECT_ID('dbo.nguoi_dan', 'U') IS NOT NULL
    DROP TABLE dbo.nguoi_dan;
GO

CREATE TABLE dbo.nguoi_dan
(
    id INT IDENTITY(1,1) PRIMARY KEY,

    ho_ten NVARCHAR(100) NOT NULL,

    gioi_tinh NVARCHAR(10) NOT NULL
        CHECK (gioi_tinh IN (N'Nam', N'Nu')),

    so_dien_thoai VARCHAR(10) NOT NULL,

    huyen NVARCHAR(50) NOT NULL,

    xa NVARCHAR(50) NOT NULL,

    vi_do DECIMAL(9,6) NOT NULL,

    kinh_do DECIMAL(9,6) NOT NULL,

    nghe_nghiep NVARCHAR(50),

    dan_toc NVARCHAR(20),

    tuoi INT DEFAULT(30),

    zalo_id VARCHAR(50),

    email VARCHAR(100),

    nhan_canh_bao BIT DEFAULT(1),

    ngay_tao DATETIME2 DEFAULT(GETDATE())
);
GO
/*
    fk.name AS ForeignKey,
    OBJECT_NAME(fk.parent_object_id) AS BangCon
FROM sys.foreign_keys fk
WHERE OBJECT_NAME(fk.referenced_object_id) = 'nguoi_dan';
SELECT name
FROM sys.foreign_keys
WHERE parent_object_id = OBJECT_ID('dbo.notification_logs');
DROP TABLE dbo.notification_logs;
GO

DROP TABLE dbo.nguoi_dan;
GO */

SET IDENTITY_INSERT dbo.nguoi_dan ON;
INSERT INTO nguoi_dan (id, ho_ten, gioi_tinh, so_dien_thoai, huyen, xa, vi_do, kinh_do, nghe_nghiep, dan_toc, tuoi, zalo_id, email, nhan_canh_bao) VALUES
(1, N'Trần Công Huy', N'Nam', '3292711244', N'Mường Chà', N'Sá Tổng', 21.656962, 102.339804, N'Lâm nghiệp', N'Thái', 27, 'ZALO_74227', 'nguyenphuong65478@gmail.com', 1),
(2, N'Bùi Thanh Yến', N'Nu', '1376534622', N'Mường Nhé', N'Na Son', 21.493905, 102.838469, N'Công nhân', N'HMong', 34, 'ZALO_40944', 'qanghuyvtpt@gmail.com', 1)

SET IDENTITY_INSERT dbo.nguoi_dan OFF;
GO




-- Create notification_logs table
CREATE TABLE dbo.notification_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nguoi_dan_id INT NOT NULL FOREIGN KEY REFERENCES dbo.nguoi_dan(id) ON DELETE CASCADE,
    warning_id NVARCHAR(100) NOT NULL,
    send_time DATETIME2 DEFAULT GETDATE(),
    status VARCHAR(20) NOT NULL
);
GO
