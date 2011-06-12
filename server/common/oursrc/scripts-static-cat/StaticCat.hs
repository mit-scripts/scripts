{-# LANGUAGE DeriveDataTypeable, ViewPatterns #-}
{-# OPTIONS_GHC -O2 -Wall #-}

import Prelude hiding (catch)
import Control.Applicative
import Control.Monad
import Control.Monad.CatchIO
import qualified Data.ByteString.Lazy as B
import Data.ByteString.Lazy.Char8 (pack)
import Data.Char
import Data.Dynamic
import Data.Int
import Data.List (unfoldr)
import Data.List.Split (splitOn)
import Data.Maybe (fromJust, isNothing, isJust)
import qualified Data.Map as M
import Data.Time.Clock.POSIX
import Data.Time.Format
import Network.CGI hiding (ContentType)
import Numeric
import System.FilePath
import System.IO
import System.IO.Error (isDoesNotExistError, isPermissionError)
import System.IO.Unsafe
import System.Locale
import System.Posix
import System.Posix.Handle
import System.Random

type Encoding = String
type ContentType = String

encodings :: M.Map String Encoding
encodings = M.fromList [
             (".bz2", "bzip2"),
             (".gz", "gzip"),
             (".z", "compress")
            ]

types :: M.Map String ContentType
types = M.fromList [
         (".avi", "video/x-msvideo"),
         (".css", "text/css"),
         (".doc", "application/msword"),
         (".docm", "application/vnd.ms-word.document.macroEnabled.12"),
         (".docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
         (".dot", "application/msword"),
         (".dotm", "application/vnd.ms-word.template.macroEnabled.12"),
         (".dotx", "application/vnd.openxmlformats-officedocument.wordprocessingml.template"),
         (".gif", "image/gif"),
         (".htm", "text/html"),
         (".html", "text/html"),
         (".ico", "image/vnd.microsoft.icon"),
         (".il", "application/octet-stream"),
         (".jar", "application/java-archive"),
         (".jpeg", "image/jpeg"),
         (".jpg", "image/jpeg"),
         (".js", "application/x-javascript"),
         (".mid", "audio/midi"),
         (".midi", "audio/midi"),
         (".mov", "video/quicktime"),
         (".mp3", "audio/mpeg"),
         (".mpeg", "video/mpeg"),
         (".mpg", "video/mpeg"),
         (".odb", "application/vnd.oasis.opendocument.database"),
         (".odc", "application/vnd.oasis.opendocument.chart"),
         (".odf", "application/vnd.oasis.opendocument.formula"),
         (".odg", "application/vnd.oasis.opendocument.graphics"),
         (".odi", "application/vnd.oasis.opendocument.image"),
         (".odm", "application/vnd.oasis.opendocument.text-master"),
         (".odp", "application/vnd.oasis.opendocument.presentation"),
         (".ods", "application/vnd.oasis.opendocument.spreadsheet"),
         (".odt", "application/vnd.oasis.opendocument.text"),
         (".otf", "application/octet-stream"),
         (".otg", "application/vnd.oasis.opendocument.graphics-template"),
         (".oth", "application/vnd.oasis.opendocument.text-web"),
         (".otp", "application/vnd.oasis.opendocument.presentation-template"),
         (".ots", "application/vnd.oasis.opendocument.spreadsheet-template"),
         (".ott", "application/vnd.oasis.opendocument.text-template"),
         (".pdf", "application/pdf"),
         (".png", "image/png"),
         (".pot", "application/vnd.ms-powerpoint"),
         (".potm", "application/vnd.ms-powerpoint.template.macroEnabled.12"),
         (".potx", "application/vnd.openxmlformats-officedocument.presentationml.template"),
         (".ppa", "application/vnd.ms-powerpoint"),
         (".ppam", "application/vnd.ms-powerpoint.addin.macroEnabled.12"),
         (".pps", "application/vnd.ms-powerpoint"),
         (".ppsm", "application/vnd.ms-powerpoint.slideshow.macroEnabled.12"),
         (".ppsx", "application/vnd.openxmlformats-officedocument.presentationml.slideshow"),
         (".ppt", "application/vnd.ms-powerpoint"),
         (".pptm", "application/vnd.ms-powerpoint.presentation.macroEnabled.12"),
         (".pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
         (".ps", "application/postscript"),
         (".svg", "image/svg+xml"),
         (".swf", "application/x-shockwave-flash"),
         (".tar", "application/x-tar"),
         (".tgz", "application/x-gzip"),
         (".tif", "image/tiff"),
         (".tiff", "image/tiff"),
         (".ttf", "application/octet-stream"),
         (".wav", "audio/x-wav"),
         (".wmv", "video/x-ms-wmv"),
         (".xaml", "application/xaml+xml"),
         (".xap", "application/x-silverlight-app"),
         (".xhtml", "application/xhtml+xml"),
         (".xla", "application/vnd.ms-excel"),
         (".xlam", "application/vnd.ms-excel.addin.macroEnabled.12"),
         (".xls", "application/vnd.ms-excel"),
         (".xlsb", "application/vnd.ms-excel.sheet.binary.macroEnabled.12"),
         (".xlsm", "application/vnd.ms-excel.sheet.macroEnabled.12"),
         (".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
         (".xlt", "application/vnd.ms-excel"),
         (".xltm", "application/vnd.ms-excel.template.macroEnabled.12"),
         (".xltx", "application/vnd.openxmlformats-officedocument.spreadsheetml.template"),
         (".xml", "text/xml"),
         (".xsl", "text/xml"),
         (".zip", "application/zip")
        ]

data MyError = NotModified | Forbidden | NotFound | BadMethod | BadRange
    deriving (Show, Typeable)

instance Exception MyError

outputMyError :: MyError -> CGI CGIResult
outputMyError NotModified = setStatus 304 "Not Modified" >> outputNothing
outputMyError Forbidden = outputError 403 "Forbidden" []
outputMyError NotFound = outputError 404 "Not Found" []
outputMyError BadMethod = outputError 405 "Method Not Allowed" []
outputMyError BadRange = outputError 416 "Requested Range Not Satisfiable" []

-- | Nothing if type is not whitelisted.
checkExtension :: FilePath -> Maybe (Maybe Encoding, ContentType)
checkExtension file =
  let (base, ext) = splitExtension file
      (file', enc) = case M.lookup (map toLower ext) encodings of
                        Nothing -> (file, Nothing)
                        Just e -> (base, Just e)
      (_, ext') = splitExtension file'
   in case M.lookup (map toLower ext') types of
            Nothing -> Nothing
            Just e -> Just (enc, e)

checkMethod :: CGI CGIResult -> CGI CGIResult
checkMethod rOutput = do
  m <- requestMethod
  case m of
    "HEAD" -> rOutput >> outputNothing
    "GET" -> rOutput
    "POST" -> rOutput
    _ -> throw BadMethod

httpDate :: String
httpDate = "%a, %d %b %Y %H:%M:%S %Z"
formatHTTPDate :: EpochTime -> String
formatHTTPDate = formatTime defaultTimeLocale httpDate .
                 posixSecondsToUTCTime . realToFrac
parseHTTPDate :: String -> Maybe EpochTime
parseHTTPDate = (fromInteger . floor . utcTimeToPOSIXSeconds <$>) .
                parseTime defaultTimeLocale httpDate

checkModified :: EpochTime -> CGI ()
checkModified mTime = do
  setHeader "Last-Modified" $ formatHTTPDate mTime
  (requestHeader "If-Modified-Since" >>=) $ maybe (return ()) $ \ims ->
      when (parseHTTPDate ims >= Just mTime) $ throw NotModified

checkIfRange :: EpochTime -> CGI (Maybe ())
checkIfRange mTime = do
  (requestHeader "If-Range" >>=) $ maybe (return $ Just ()) $ \ir ->
      return $ if parseHTTPDate ir == Just mTime then Just () else Nothing

-- | parseRanges string size returns a list of ranges, or Nothing if parse fails.
parseRanges :: String -> FileOffset -> Maybe [(FileOffset, FileOffset)]
parseRanges (splitAt 6 -> ("bytes=", ranges)) size =
    mapM parseOneRange $ splitOn "," ranges
    where parseOneRange ('-':(readDec -> [(len, "")])) =
            Just (max 0 (size - len), size - 1)
          parseOneRange (readDec -> [(a, "-")]) =
            Just (a, size - 1)
          parseOneRange (readDec -> [(a, '-':(readDec -> [(b, "")]))]) =
            Just (a, min (size - 1) b)
          parseOneRange _ = Nothing
parseRanges _ _ = Nothing

checkRanges :: EpochTime -> FileOffset -> CGI (Maybe [(FileOffset, FileOffset)])
checkRanges mTime size = do
  setHeader "Accept-Ranges" "bytes"
  (requestHeader "Range" >>=) $ maybe (return Nothing) $ \range -> do
  (checkIfRange mTime >>=) $ maybe (return Nothing) $ \() -> do
    case parseRanges range size of
      Just rs | all (\(a, b) -> a <= b) rs -> return $ Just rs
      Just _ -> throw BadRange
      Nothing -> return Nothing

outputAll :: Handle -> FileOffset -> ContentType -> CGI CGIResult
outputAll h size ctype = do
  setHeader "Content-Type" ctype
  setHeader "Content-Length" $ show size
  outputFPS =<< liftIO (B.hGetContents h)

-- | Lazily read a given number of bytes from the handle into a
-- 'ByteString', then close the handle.
hGetClose :: Handle -> Int64 -> IO B.ByteString
hGetClose h len = do
  contents <- B.hGetContents h
  end <- unsafeInterleaveIO (hClose h >> return B.empty)
  return (B.append (B.take len contents) end)

outputRange :: Handle -> FileOffset -> ContentType -> Maybe [(FileOffset, FileOffset)] -> CGI CGIResult
outputRange h size ctype Nothing = outputAll h size ctype
outputRange h size ctype (Just [(a, b)]) = do
  let len = b - a + 1

  setStatus 206 "Partial Content"
  setHeader "Content-Type" ctype
  setHeader "Content-Range" $
   "bytes " ++ show a ++ "-" ++ show b ++ "/" ++ show size
  setHeader "Content-Length" $ show len
  liftIO $ hSeek h AbsoluteSeek (fromIntegral a)
  outputFPS =<< liftIO (hGetClose h (fromIntegral len))
outputRange h size ctype (Just rs) = do
  seed <- liftIO getStdGen
  let ints = take 16 $ unfoldr (Just . random) seed :: [Int]
      sep  = concat $ map (flip showHex "" . (`mod` 16)) ints
  setStatus 206 "Partial Content"

  setHeader "Content-Type" $ "multipart/byteranges; boundary=" ++ sep
  -- Need Content-Length? RFC doesn't seem to mandate it...
  chunks <- liftIO $ sequence $ map readChunk rs
  let parts = map (uncurry $ mkPartHeader sep) (zip rs chunks)
      body = B.concat [ pack "\r\n"
                      , B.concat parts
                      , pack "--", pack sep, pack "--\r\n"
                      ]
  end <- liftIO $ unsafeInterleaveIO (hClose h >> return B.empty)
  -- TODO figure out how to guarantee handle is ALWAYS closed, and NEVER before
  -- reading is finished...
  outputFPS (B.append body end)
   where readChunk :: (FileOffset, FileOffset) -> IO B.ByteString
         readChunk (a, b) = do
            hSeek h AbsoluteSeek (fromIntegral a)
            -- Carful here, hGetContents makes the handle unusable afterwards.
            -- TODO Anders says use hGetSome or some other way lazy way
            B.hGet h (fromIntegral $ b - a + 1)
         mkPartHeader :: String -> (FileOffset, FileOffset) -> B.ByteString -> B.ByteString
         mkPartHeader sep (a, b) chunk = B.concat [ pack "--" , pack sep
                                                  , pack "\r\nContent-Type: ", pack ctype
                                                  , pack "\r\nContent-Range: bytes "
                                                  , pack $ show a, pack "-", pack $ show b
                                                  , pack "/", pack $ show size
                                                  , pack "\r\n\r\n", chunk, pack "\r\n"
                                                  ]


serveFile :: FilePath -> CGI CGIResult
serveFile file = (`catch` outputMyError) $ do
  let menctype = checkExtension file
  when (isNothing menctype) $ throw Forbidden
  let (menc, ctype) = fromJust menctype
  when (isJust menc) $ setHeader "Content-Encoding" (fromJust menc)

  checkMethod $ do

  let handleOpenError e =
          if isDoesNotExistError e then throw NotFound
          else if isPermissionError e then throw Forbidden
          else throw e
  h <- liftIO (openBinaryFile file ReadMode) `catch` handleOpenError
  (`onException` liftIO (hClose h)) $ do

  status <- liftIO $ hGetStatus h
  let mTime = modificationTime status
      size = fileSize status
  checkModified mTime

  ranges <- checkRanges mTime size
  outputRange h size ctype ranges

main :: IO ()
main = runCGI $ handleErrors $ serveFile =<< pathTranslated
